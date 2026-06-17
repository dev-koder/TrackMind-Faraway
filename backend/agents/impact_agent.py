from agents.base_agent import BaseAgent
from agents.prompts import IMPACT_PROMPT


class ImpactAgent(BaseAgent):
    def __init__(self, broadcast):
        super().__init__("impact", IMPACT_PROMPT, broadcast)

    async def run_with_fallback(self, context: dict) -> dict:
        data = await super().run_with_fallback(context)

        await self.broadcast("impact_update", {
            "total_passengers_affected": data["total_passengers_affected"],
            "missed_connections": data["missed_connections"],
            "trains_impacted": len(context.get("cascade", {}).get("affected_trains", [])) or 3,
            "impact_score": data["impact_score"],
        })

        return data

    def mock_response(self, context: dict) -> dict:
        cascade = context.get("cascade", {})
        affected = cascade.get("affected_trains", [])
        trains_impacted = len(affected) or 3

        return {
            "agent": "impact",
            "total_passengers_affected": 2847,
            "missed_connections": 203,
            "high_priority_trains": [
                "12302 Rajdhani — 847 passengers",
                "12301 Rajdhani — 1104 passengers",
            ],
            "impact_score": 8.2,
            "narrative": (
                f"Approximately 2,847 passengers affected across {trains_impacted} trains. "
                "203 passengers at risk of missing connections within the 45-minute window."
            ),
            "calculation_notes": (
                "12301: 1200×0.92=1104; 12302: 1200×0.89=1068; 13005: 2200×0.73=1606; "
                "deduplicated overlap ≈ 2847 total affected; connection misses ≈ 203"
            ),
        }

    def _audit_action(self, data: dict) -> str:
        return "Impact quantified"

    def _audit_detail(self, data: dict) -> str:
        return (
            f"{data['total_passengers_affected']:,} passengers — "
            f"score {data['impact_score']}/10"
        )
