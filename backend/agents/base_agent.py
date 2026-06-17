import uuid
from datetime import datetime, timezone
from typing import Awaitable, Callable, Dict, Optional

from agents.claude_client import call_claude


BroadcastFn = Callable[[str, dict], Awaitable[None]]


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, broadcast: BroadcastFn):
        self.name = name
        self.system_prompt = system_prompt
        self.broadcast = broadcast

    async def run(self, context: dict) -> dict:
        user_content = json_dumps(context)
        return await call_claude(self.system_prompt, user_content)

    def mock_response(self, context: dict) -> dict:
        raise NotImplementedError

    async def run_with_fallback(self, context: dict) -> dict:
        await self.broadcast("agent_fire", {
            "agent": self.name,
            "status": "thinking",
        })

        status = "done"
        try:
            data = await self.run(context)
        except Exception:
            data = self.mock_response(context)
            status = "fallback"

        await self.broadcast("agent_result", {
            "agent": self.name,
            "status": status,
            "data": data,
        })

        await self.broadcast("audit_entry", {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "agent": self.name,
            "action": self._audit_action(data),
            "detail": self._audit_detail(data),
            "reasoning": self._audit_reasoning(data),
        })

        return data

    def _audit_action(self, data: dict) -> str:
        return f"{self.name} agent completed"

    def _audit_detail(self, data: dict) -> str:
        return str(data.get("message") or data.get("narrative") or data.get("without_intervention", ""))

    def _audit_reasoning(self, data: dict) -> str:
        return str(
            data.get("reasoning")
            or data.get("calculation_notes")
            or data.get("recommendation_reason")
            or data.get("operations_log")
            or ""
        )


def json_dumps(obj: dict) -> str:
    import json
    return json.dumps(obj, indent=2, default=str)
