from agents.base_agent import BaseAgent
from agents.prompts import CASCADE_PROMPT


class CascadeAgent(BaseAgent):
    def __init__(self, broadcast):
        super().__init__("cascade", CASCADE_PROMPT, broadcast)

    def mock_response(self, context: dict) -> dict:
        monitor = context.get("monitor", {})
        delay = monitor.get("delay_minutes", 47)

        if delay >= 60:
            severity = "SEVERE"
        elif delay >= 30:
            severity = "MAJOR"
        elif delay >= 15:
            severity = "MODERATE"
        else:
            severity = "LOW"

        return {
            "agent": "cascade",
            "affected_trains": [
                {
                    "train_id": "12302",
                    "train_name": "New Delhi Rajdhani Express",
                    "predicted_delay_minutes": 34,
                    "reason": "Platform conflict at MGS",
                },
                {
                    "train_id": "13005",
                    "train_name": "Howrah Amritsar Express",
                    "predicted_delay_minutes": 22,
                    "reason": "Track dependency at ALD",
                },
                {
                    "train_id": "12305",
                    "train_name": "Howrah Poorva Express",
                    "predicted_delay_minutes": 18,
                    "reason": "Single-track bottleneck at ALD-MGS",
                },
            ],
            "affected_stations": ["ALD", "MGS", "PNBE"],
            "cascade_severity": severity,
            "without_intervention": "3 trains delayed, 3 stations impacted",
        }

    def _audit_action(self, data: dict) -> str:
        return "Cascade predicted"

    def _audit_detail(self, data: dict) -> str:
        count = len(data.get("affected_trains", []))
        stations = ", ".join(data.get("affected_stations", []))
        return f"{count} trains affected — {stations}"
