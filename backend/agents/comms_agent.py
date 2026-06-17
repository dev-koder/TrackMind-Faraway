from agents.base_agent import BaseAgent
from agents.prompts import COMMS_PROMPT


class CommsAgent(BaseAgent):
    def __init__(self, broadcast):
        super().__init__("comms", COMMS_PROMPT, broadcast)

    async def run_with_fallback(self, context: dict) -> dict:
        data = await super().run_with_fallback(context)

        await self.broadcast("comms_ready", {
            "station_announcement": data["station_announcement"],
            "sms_draft": data["sms_draft"],
            "operations_log": data["operations_log"],
        })

        return data

    def mock_response(self, context: dict) -> dict:
        monitor = context.get("monitor", {})
        train_id = monitor.get("train_id", "12301")
        delay = monitor.get("delay_minutes", 47)
        station = monitor.get("station", "CNB")

        return {
            "agent": "comms",
            "station_announcement": {
                "english": (
                    f"Attention passengers. Train {train_id} Rajdhani Express "
                    f"is running {delay} minutes late at {station}. "
                    "We regret the inconvenience. Updated arrival information will follow."
                ),
                "hindi": (
                    "यात्रियों का ध्यान आकर्षित किया जाता है कि ट्रेन 12301 हावड़ा राजधानी "
                    f"कानपुर सेंट्रल पर {delay} मिनट विलंब से है। असुविधा के लिए खेद है।"
                ),
            },
            "sms_draft": (
                f"IRCTC ALERT: Train {train_id} delayed {delay} mins at {station}. "
                "New arrival ALD: 17:45. -TrackMind"
            ),
            "operations_log": (
                f"14:32 | DELAY EVENT | {train_id} | {station} | +{delay}min | "
                "CASCADE: 3 trains | RESPONSE: Option A selected | COMMS: Dispatched"
            ),
        }

    def _audit_action(self, data: dict) -> str:
        return "Comms drafted"

    def _audit_detail(self, data: dict) -> str:
        return "Announcements drafted — EN + HI + SMS"
