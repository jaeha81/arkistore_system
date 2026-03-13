"""
GitHub REST API 클라이언트 래퍼
실제 구현: Phase 5
현재: Mock adapter로 대체
"""
from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class GithubIssuePayload:
    title: str
    body: str
    labels: list[str]
    repository: str


@dataclass
class GithubIssueResult:
    issue_number: int
    issue_url: str
    state: str


class GithubClient:
    """실제 GitHub API 연동 클라이언트 (Phase 5에서 완성)"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        """GitHub 이슈 생성"""
        owner_repo = payload.repository
        url = f"{self.BASE_URL}/repos/{owner_repo}/issues"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json={
                    "title": payload.title,
                    "body": payload.body,
                    "labels": payload.labels,
                },
                headers=self.headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return GithubIssueResult(
                issue_number=data["number"],
                issue_url=data["html_url"],
                state=data["state"],
            )
