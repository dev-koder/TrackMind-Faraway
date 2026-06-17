import asyncio
from typing import Awaitable, Callable, Dict, List, Optional

from agents import (
    CascadeAgent,
    CommsAgent,
    ImpactAgent,
    MonitorAgent,
    ResponseAgent,
)

BroadcastFn = Callable[[str, dict], Awaitable[None]]


class AgentOrchestrator:
    def __init__(self, broadcast: BroadcastFn, corridor_data: dict):
        self.broadcast = broadcast
        self.corridor_data = corridor_data
        self.audit_log: List[dict] = []
        self.agent_outputs: Dict[str, dict] = {}
        self._running = False
        self._lock = asyncio.Lock()

        self.monitor = MonitorAgent(broadcast)
        self.cascade = CascadeAgent(broadcast)
        self.impact = ImpactAgent(broadcast)
        self.response = ResponseAgent(broadcast)
        self.comms = CommsAgent(broadcast)

    async def run_pipeline(self, delay_event: dict) -> Dict[str, dict]:
        async with self._lock:
            if self._running:
                return self.agent_outputs
            self._running = True
            self.agent_outputs = {}

        try:
            context = {
                "delay_event": delay_event,
                "corridor": self.corridor_data,
            }

            monitor_out = await self.monitor.run_with_fallback(context)
            self.agent_outputs["monitor"] = monitor_out
            context["monitor"] = monitor_out

            cascade_out = await self.cascade.run_with_fallback(context)
            self.agent_outputs["cascade"] = cascade_out
            context["cascade"] = cascade_out

            impact_out = await self.impact.run_with_fallback(context)
            self.agent_outputs["impact"] = impact_out
            context["impact"] = impact_out

            response_out = await self.response.run_with_fallback(context)
            self.agent_outputs["response"] = response_out
            context["response"] = response_out

            comms_out = await self.comms.run_with_fallback(context)
            self.agent_outputs["comms"] = comms_out

            return self.agent_outputs
        finally:
            self._running = False

    def reset(self) -> None:
        self.agent_outputs = {}
        self.audit_log = []
        self._running = False
