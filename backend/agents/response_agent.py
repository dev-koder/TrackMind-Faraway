from agents.base_agent import BaseAgent
from agents.prompts import RESPONSE_PROMPT


class ResponseAgent(BaseAgent):
    def __init__(self, broadcast):
        super().__init__("response", RESPONSE_PROMPT, broadcast)

    async def run_with_fallback(self, context: dict) -> dict:
        data = await super().run_with_fallback(context)

        await self.broadcast("response_ready", {
            "options": data["options"],
            "recommendation": data["recommendation"],
            "recommendation_reason": data["recommendation_reason"],
        })

        return data

    def mock_response(self, context: dict) -> dict:
        return {
            "agent": "response",
            "options": [
                {
                    "id": "A",
                    "label": "Hold and Merge",
                    "action": "Hold Train 12302 at ALD for 18 minutes to allow connection",
                    "delay_cost_minutes": 18,
                    "passengers_saved": 203,
                    "risk": "Platform conflict at MGS if freight train is on time",
                    "optimizes_for": "passenger_service",
                },
                {
                    "id": "B",
                    "label": "Proceed and Reroute",
                    "action": "Allow 12302 to proceed, reroute affected passengers to 13005",
                    "delay_cost_minutes": 6,
                    "passengers_saved": 89,
                    "risk": "13005 may not have capacity",
                    "optimizes_for": "efficiency",
                },
            ],
            "recommendation": "A",
            "recommendation_reason": "203 vs 89 passengers saved outweighs 12-minute delay cost",
        }

    def _audit_action(self, data: dict) -> str:
        return "Response generated"

    def _audit_detail(self, data: dict) -> str:
        rec = data.get("recommendation", "A")
        saved = next(
            (o["passengers_saved"] for o in data.get("options", []) if o["id"] == rec),
            203,
        )
        return f"Option {rec} recommended — {saved} connections saved"
