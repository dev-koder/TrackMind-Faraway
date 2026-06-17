import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Set

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from arbitration import arbitrate
from orchestrator import AgentOrchestrator
from simulation import SimulationEngine

load_dotenv()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

connected_clients: Set[WebSocket] = set()
simulation: Optional[SimulationEngine] = None
orchestrator: Optional[AgentOrchestrator] = None
audit_log: list = []
pipeline_task: Optional[asyncio.Task] = None
arbitration_result: Optional[dict] = None

corridor_data: dict = {}
with open(Path(__file__).parent / "data" / "corridor.json", encoding="utf-8") as f:
    corridor_data = json.load(f)


async def broadcast(event: str, payload: dict) -> None:
    if event == "audit_entry":
        audit_log.append(payload)

    message = json.dumps({
        "event": event,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    disconnected: Set[WebSocket] = set()
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected.add(client)
    connected_clients.difference_update(disconnected)


async def on_simulation_update(trains: list) -> None:
    await broadcast("train_update", {"trains": trains})


async def run_agent_pipeline(delay_event: dict) -> None:
    global arbitration_result
    if not orchestrator:
        return

    outputs = await orchestrator.run_pipeline(delay_event)
    result = arbitrate(outputs)
    arbitration_result = result

    await broadcast("arbitration_done", result)

    await broadcast("audit_entry", {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "agent": "arbitrate",
        "action": "Arbitration complete",
        "detail": (
            f"Option {result['recommendation']} confirmed "
            f"({result['confidence']:.0%} confidence)"
        ),
        "reasoning": f"Weighted vote breakdown: {result['vote_breakdown']}",
    })


async def on_delay_detected(event: dict) -> None:
    global pipeline_task
    if pipeline_task and not pipeline_task.done():
        return
    pipeline_task = asyncio.create_task(run_agent_pipeline(event))


async def trigger_delay_pipeline(delay_event: dict) -> None:
    global pipeline_task
    if pipeline_task and not pipeline_task.done():
        pipeline_task.cancel()
        try:
            await pipeline_task
        except asyncio.CancelledError:
            pass
    pipeline_task = asyncio.create_task(run_agent_pipeline(delay_event))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global simulation, orchestrator
    orchestrator = AgentOrchestrator(broadcast=broadcast, corridor_data=corridor_data)
    simulation = SimulationEngine(
        on_delay_detected=on_delay_detected,
        on_update=on_simulation_update,
    )
    await simulation.start()
    yield
    if simulation:
        await simulation.stop()


app = FastAPI(title="TrackMind API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InjectDelayRequest(BaseModel):
    scenario_id: Optional[str] = None
    train_id: Optional[str] = None
    delay_minutes: Optional[int] = None
    at_station: Optional[str] = None
    reason: Optional[str] = None


@app.get("/")
async def root():
    return {"status": "ok", "service": "TrackMind"}


@app.get("/api/status")
async def get_status():
    if not simulation:
        return {"simulation_running": False, "sim_time": "00:00", "delay_active": False, "trains": [], "connected_clients": len(connected_clients)}
    status = simulation.get_status()
    status["connected_clients"] = len(connected_clients)
    return status


@app.post("/api/inject-delay")
async def inject_delay(body: InjectDelayRequest):
    if not simulation:
        return {"status": "error", "message": "Simulation not running"}

    if body.scenario_id:
        scenario = next(
            (s for s in corridor_data["delay_scenarios"] if s["id"] == body.scenario_id),
            None,
        )
        if not scenario:
            return {"status": "error", "message": f"Unknown scenario: {body.scenario_id}"}
        train_id = scenario["train_id"]
        delay_minutes = scenario["delay_minutes"]
        at_station = scenario["at_station"]
        reason = scenario.get("reason", "Operational delay")
    else:
        if not body.train_id or body.delay_minutes is None or not body.at_station:
            return {"status": "error", "message": "Provide scenario_id or train_id, delay_minutes, at_station"}
        train_id = body.train_id
        delay_minutes = body.delay_minutes
        at_station = body.at_station
        reason = body.reason or "Operational delay"

    simulation.inject_delay(train_id, delay_minutes, at_station)
    simulation._delay_triggered = True

    delay_event = simulation._build_delay_event(train_id)
    delay_event["reason"] = reason

    await trigger_delay_pipeline(delay_event)

    event_id = f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    return {
        "status": "accepted",
        "delay_event_id": event_id,
        "message": "Delay injected. Agents will fire within 3 seconds.",
    }


@app.post("/api/reset")
async def reset_simulation():
    global pipeline_task, arbitration_result

    if pipeline_task and not pipeline_task.done():
        pipeline_task.cancel()
        try:
            await pipeline_task
        except asyncio.CancelledError:
            pass
    pipeline_task = None
    arbitration_result = None

    if simulation:
        simulation.reset()
    if orchestrator:
        orchestrator.reset()
    audit_log.clear()

    await broadcast("simulation_reset", {})

    return {
        "status": "reset",
        "message": "Simulation reset to initial state.",
    }


@app.get("/api/corridor")
async def get_corridor():
    return corridor_data


@app.get("/api/audit-log")
async def get_audit_log():
    return {"entries": audit_log}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    if simulation:
        await websocket.send_text(json.dumps({
            "event": "train_update",
            "payload": {"trains": simulation.get_train_positions()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))

    try:
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        connected_clients.discard(websocket)
