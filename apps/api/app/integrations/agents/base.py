"""
AI Agent Provider 기본 인터페이스
OpenAI / Anthropic / Gemini 전환 가능 구조
MVP에서는 사용하지 않음 - Phase 2 이후
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class AgentRequest:
    messages: list[AgentMessage]
    model: str | None = None
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: str | None = None


@dataclass
class AgentResponse:
    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"


class BaseAgentProvider(ABC):
    """AI 에이전트 Provider 공통 인터페이스"""

    @abstractmethod
    async def complete(self, request: AgentRequest) -> AgentResponse:
        ...

    @abstractmethod
    async def stream(self, request: AgentRequest):
        """스트리밍 응답 (제너레이터)"""
        ...


class MockAgentProvider(BaseAgentProvider):
    """테스트/개발용 Mock Provider"""

    async def complete(self, request: AgentRequest) -> AgentResponse:
        last_message = request.messages[-1].content if request.messages else ""
        return AgentResponse(
            content=f"[MOCK AGENT RESPONSE] Input: {last_message[:50]}...",
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
        )

    async def stream(self, request: AgentRequest):
        yield "[MOCK STREAM] "
        yield "Response token by token"


def get_agent_provider(provider: str = "mock") -> BaseAgentProvider:
    """
    Provider 선택
    - "openai": OpenAI GPT
    - "anthropic": Anthropic Claude
    - "gemini": Google Gemini
    - "mock": Mock (기본값)
    """
    if provider == "openai":
        from app.integrations.agents.provider_openai import OpenAIProvider
        return OpenAIProvider()
    if provider == "anthropic":
        from app.integrations.agents.provider_anthropic import AnthropicProvider
        return AnthropicProvider()
    if provider == "gemini":
        from app.integrations.agents.provider_gemini import GeminiProvider
        return GeminiProvider()
    return MockAgentProvider()
