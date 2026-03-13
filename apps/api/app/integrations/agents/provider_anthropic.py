"""
provider_anthropic placeholder
Phase 2 이후 실 구현
"""
from app.integrations.agents.base import AgentRequest, AgentResponse, BaseAgentProvider


class Anthropic Provider(BaseAgentProvider):
    async def complete(self, request: AgentRequest) -> AgentResponse:
        raise NotImplementedError("provider_anthropic not yet implemented")

    async def stream(self, request: AgentRequest):
        raise NotImplementedError("provider_anthropic not yet implemented")
        yield  # make it a generator
