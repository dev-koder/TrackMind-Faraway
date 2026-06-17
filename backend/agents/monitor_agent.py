from agents.base_agent import BaseAgent
from agents.prompts import MONITOR_PROMPT


class MonitorAgent(BaseAgent):
    def __init__(self, broadcast):
        super().__init__("monitor", MONITOR_PROMPT, broadcast)

    def mock_response(self, context: dict) -> dict:
        event = context.get("delay_event", {})
        delay = event.get("delay_minutes", 47)
        train_id = event.get("train_id", "12301")
        train_name = event.get("train_name", "Howrah Rajdhani Express")
        station = event.get("station_id", "CNB")
        timestamp = event.get("timestamp", "2026-06-14T14:32:00")

        if delay > 60:
            severity = "CRITICAL"
        elif delay > 30:
            severity = "HIGH"
        elif delay > 15:
            severity = "MODERATE"
        else:
            severity = "MINOR"

        return {
            "agent": "monitor",
            "train_id": train_id,
            "train_name": train_name,
            "station": station,
            "delay_minutes": delay,
            "severity": severity,
            "timestamp": timestamp,
            "message": f"{train_name} delayed {delay} minutes at {station}",
            "reasoning": f"Scheduled vs actual arrival delta = +{delay} min at {station}",
        }

    def _audit_action(self, data: dict) -> str:
        return "Delay detected"

    def _audit_detail(self, data: dict) -> str:
        return f"Train {data['train_id']} delayed {data['delay_minutes']} minutes at {data['station']}"
