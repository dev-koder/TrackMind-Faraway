import asyncio
import copy
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def _parse_time(time_str: str, base_date: datetime) -> datetime:
    """Parse HH:MM schedule time onto base_date, rolling to next day if needed."""
    hour, minute = map(int, time_str.split(":"))
    result = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if result < base_date:
        result += timedelta(days=1)
    return result


def _format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _minutes_between(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 60


class SimulationEngine:
    def __init__(
        self,
        on_delay_detected: Optional[Callable] = None,
        on_update: Optional[Callable] = None,
    ):
        self.data_path = Path(__file__).parent / "data" / "corridor.json"
        with open(self.data_path, encoding="utf-8") as f:
            self.corridor_data = json.load(f)

        self.config = self.corridor_data["simulation_config"]
        self.stations = {s["id"]: s for s in self.corridor_data["stations"]}
        self.train_definitions = {t["id"]: t for t in self.corridor_data["trains"]}

        self.time_multiplier = int(
            os.getenv("SIMULATION_SPEED", str(self.config["time_multiplier"]))
        )
        self.update_interval = self.config["update_interval_seconds"]
        self.delay_threshold = self.config["delay_cascade_threshold_minutes"]

        self.on_delay_detected = on_delay_detected
        self.on_update = on_update

        self.trains: Dict[str, dict] = {}
        self.sim_time: datetime = datetime(2026, 6, 14, 16, 0, 0)
        self.base_date = self.sim_time.date()
        self.running = False
        self.delay_active = False
        self._loop_task: Optional[asyncio.Task] = None
        self._delay_triggered = False
        self._injected_delays: List[dict] = []

        self._init_trains()

    def _init_trains(self) -> None:
        self.trains = {}
        for train_id, definition in self.train_definitions.items():
            schedule = definition["schedule"]
            first = schedule[0]
            current_station = first["station"]
            next_station = schedule[1]["station"] if len(schedule) > 1 else first["station"]

            self.trains[train_id] = {
                "train_id": train_id,
                "train_name": definition["name"],
                "definition": definition,
                "current_station": current_station,
                "next_station": next_station,
                "segment_index": 0,
                "progress_pct": 0.0,
                "delay_minutes": 0,
                "status": "on_time",
                "color": definition["color"],
                "scheduled_arrival": None,
                "actual_arrival": None,
                "injected_at_station": None,
            }

    def _get_schedule_datetimes(self, train_id: str) -> List[dict]:
        """Build schedule entries with parsed datetimes."""
        definition = self.train_definitions[train_id]
        entries = []
        ref = datetime.combine(self.base_date, datetime.min.time()).replace(
            hour=16, minute=0
        )
        prev_dt = ref

        for entry in definition["schedule"]:
            parsed = {}
            if "arrival" in entry:
                arr = _parse_time(entry["arrival"], prev_dt)
                parsed["arrival"] = arr
                prev_dt = arr
            if "departure" in entry:
                dep = _parse_time(entry["departure"], prev_dt)
                parsed["departure"] = dep
                prev_dt = dep
            parsed["station"] = entry["station"]
            entries.append(parsed)
        return entries

    def _update_train_position(self, train_id: str) -> None:
        train = self.trains[train_id]
        schedule = self._get_schedule_datetimes(train_id)
        effective_time = self.sim_time - timedelta(minutes=train["delay_minutes"])

        current_idx = 0
        for i in range(len(schedule) - 1):
            dep_time = schedule[i].get("departure") or schedule[i].get("arrival")
            arr_time = schedule[i + 1].get("arrival") or schedule[i + 1].get("departure")
            if dep_time and arr_time and dep_time <= effective_time <= arr_time:
                current_idx = i
                break
            if i == len(schedule) - 2:
                current_idx = i

        from_station = schedule[current_idx]["station"]
        to_station = schedule[current_idx + 1]["station"] if current_idx + 1 < len(schedule) else from_station

        dep_time = schedule[current_idx].get("departure") or schedule[current_idx].get("arrival")
        arr_time = (
            schedule[current_idx + 1].get("arrival")
            if current_idx + 1 < len(schedule)
            else dep_time
        )

        progress = 0.0
        if dep_time and arr_time and dep_time != arr_time:
            total = _minutes_between(dep_time, arr_time)
            elapsed = _minutes_between(dep_time, effective_time)
            progress = min(100.0, max(0.0, (elapsed / total) * 100 if total > 0 else 0))

        if effective_time >= (arr_time or dep_time) and current_idx + 1 < len(schedule):
            train["current_station"] = to_station
            train["next_station"] = (
                schedule[current_idx + 2]["station"]
                if current_idx + 2 < len(schedule)
                else to_station
            )
            train["segment_index"] = current_idx + 1
            train["progress_pct"] = 100.0
        else:
            train["current_station"] = from_station
            train["next_station"] = to_station
            train["segment_index"] = current_idx
            train["progress_pct"] = progress

        next_arr = schedule[current_idx + 1].get("arrival") if current_idx + 1 < len(schedule) else None
        train["scheduled_arrival"] = _format_time(next_arr) if next_arr else None

        if train["delay_minutes"] > 0:
            actual = self.sim_time
            train["actual_arrival"] = _format_time(actual)
        else:
            train["actual_arrival"] = train["scheduled_arrival"]

        if train["delay_minutes"] > 60:
            train["status"] = "severely_delayed"
        elif train["delay_minutes"] > 10:
            train["status"] = "delayed"
        else:
            train["status"] = "on_time"

    def _update_all_positions(self) -> None:
        for train_id in self.trains:
            self._update_train_position(train_id)

    def inject_delay(self, train_id: str, delay_minutes: int, at_station: str) -> None:
        if train_id not in self.trains:
            raise ValueError(f"Unknown train: {train_id}")

        train = self.trains[train_id]
        train["delay_minutes"] = delay_minutes
        train["injected_at_station"] = at_station
        train["current_station"] = at_station
        train["status"] = "severely_delayed" if delay_minutes > 60 else "delayed"

        self.delay_active = True
        self._delay_triggered = False
        self._injected_delays.append({
            "train_id": train_id,
            "delay_minutes": delay_minutes,
            "at_station": at_station,
        })

    def reset(self) -> None:
        self._init_trains()
        self.sim_time = datetime(2026, 6, 14, 16, 0, 0)
        self.base_date = self.sim_time.date()
        self.delay_active = False
        self._delay_triggered = False
        self._injected_delays = []

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._loop_task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self.running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            self._loop_task = None

    async def _run_loop(self) -> None:
        while self.running:
            try:
                self.sim_time += timedelta(minutes=self.update_interval)
                self._update_all_positions()

                if self.on_update:
                    result = self.on_update(self.get_train_positions())
                    if asyncio.iscoroutine(result):
                        await result

                await self._check_delays()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(3)
                continue

    async def _check_delays(self) -> None:
        if self._delay_triggered:
            return

        for train_id, train in self.trains.items():
            if train["delay_minutes"] > self.delay_threshold:
                self._delay_triggered = True
                if self.on_delay_detected:
                    event = self._build_delay_event(train_id)
                    result = self.on_delay_detected(event)
                    if asyncio.iscoroutine(result):
                        await result
                break

    def _build_delay_event(self, train_id: str) -> dict:
        train = self.trains[train_id]
        station_id = train.get("injected_at_station") or train["current_station"]
        station = self.stations.get(station_id, {})
        return {
            "train_id": train_id,
            "train_name": train["train_name"],
            "station_id": station_id,
            "station_name": station.get("name", station_id),
            "delay_minutes": train["delay_minutes"],
            "severity": self._severity(train["delay_minutes"]),
            "timestamp": self.sim_time.isoformat(),
            "reason": "Operational delay",
        }

    @staticmethod
    def _severity(delay_minutes: int) -> str:
        if delay_minutes > 60:
            return "CRITICAL"
        if delay_minutes > 30:
            return "HIGH"
        if delay_minutes > 15:
            return "MODERATE"
        return "MINOR"

    def get_train_positions(self) -> List[dict]:
        positions = []
        for train_id, train in self.trains.items():
            positions.append({
                "train_id": train_id,
                "train_name": train["train_name"],
                "current_station": train["current_station"],
                "next_station": train["next_station"],
                "progress_pct": round(train["progress_pct"], 1),
                "scheduled_arrival": train["scheduled_arrival"],
                "actual_arrival": train["actual_arrival"],
                "delay_minutes": train["delay_minutes"],
                "status": train["status"],
                "color": train["color"],
            })
        return positions

    def get_status(self) -> dict:
        return {
            "simulation_running": self.running,
            "sim_time": _format_time(self.sim_time),
            "delay_active": self.delay_active,
            "trains": self.get_train_positions(),
        }
