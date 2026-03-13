"""
GitHub Adapter
서비스에서 직접 사용하는 인터페이스
Mock ↔ Real 교체 가능 구조
"""
from abc import ABC, abstractmethod

from app.integrations.github.client import (
    GithubClient,
    GithubIssuePayload,
    GithubIssueResult,
)


class BaseGithubAdapter(ABC):
    @abstractmethod
    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        ...


class GithubAdapter(BaseGithubAdapter):
    """실제 GitHub API 연동 (Phase 5에서 구현)"""

    def __init__(self, token: str):
        self.client = GithubClient(token=token)

    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        return await self.client.create_issue(payload)


class MockGithubAdapter(BaseGithubAdapter):
    """테스트/개발용 Mock - 실제 API 호출 없음"""

    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        return GithubIssueResult(
            issue_number=9999,
            issue_url=f"https://github.com/{payload.repository}/issues/9999",
            state="open",
        )


def get_github_adapter() -> BaseGithubAdapter:
    """
    의존성 주입용 팩토리
    GITHUB_TOKEN이 있으면 실제 어댑터, 없으면 Mock
    """
    from app.core.config import settings

    if settings.GITHUB_TOKEN:
        return GithubAdapter(token=settings.GITHUB_TOKEN)
    return MockGithubAdapter()
