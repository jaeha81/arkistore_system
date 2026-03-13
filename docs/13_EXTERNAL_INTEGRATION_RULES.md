# 13 EXTERNAL INTEGRATION RULES — 외부 연동 규칙

## 원칙

> 모든 외부 연동은 **Adapter-First + Mock-First** 원칙을 따른다.
> 실 연동은 명시적 승인과 자격증명 확보 후에만 구현한다.

---

## 1. GitHub Issues

| 항목 | 내용 |
|------|------|
| 용도 | 오류 이슈 생성, 이슈 상태 추적 |
| 방식 | REST API v3 (Personal Access Token) |
| 구현 위치 | integrations/github/client.py, adapter.py |
| MVP 구현 | Phase 5 |
| Mock | MockGithubAdapter (tests 전용) |

**API 사용 범위:**
```
POST /repos/{owner}/{repo}/issues    이슈 생성
GET  /repos/{owner}/{repo}/issues/{issue_number}  이슈 조회
PATCH /repos/{owner}/{repo}/issues/{issue_number} 이슈 수정
```

---

## 2. Google Sheets

| 항목 | 내용 |
|------|------|
| 용도 | 업무 데이터 export, 현업 조회/편집 |
| 방식 | Google Sheets API v4 (Service Account) |
| 구현 위치 | integrations/google/sheets_client.py |
| MVP 구현 | Phase 6 |
| Mock | MockSheetsClient (tests 전용) |

**원칙:**
- DB → Sheets: 단방향 export 기본
- Sheets → DB: 허용 범위 명시 후에만 구현
- 원본 DB는 PostgreSQL

---

## 3. Google Drive

| 항목 | 내용 |
|------|------|
| 용도 | 계약서, 인보이스, 첨부 파일 저장 |
| 방식 | Google Drive API v3 (Service Account) |
| 구현 위치 | integrations/google/drive_client.py |
| MVP 구현 | Phase 1 (presign 구조만) |
| Mock | MockDriveClient (tests 전용) |

---

## 4. S3-Compatible Storage

| 항목 | 내용 |
|------|------|
| 용도 | 파일 업로드 (Drive 대안) |
| 방식 | boto3 / S3 Presigned URL |
| 구현 위치 | integrations/storage/s3_client.py, signer.py |
| MVP 구현 | Phase 1 (presign API만) |

---

## 5. Ecount ERP

| 항목 | 내용 |
|------|------|
| 용도 | 발주/재고 연동 (미확정) |
| 방식 | 미정 (API 검토 중) |
| MVP | **Mock-only** |
| 실 연동 | 별도 승인 필요 |

> ⚠️ 검증되지 않은 Ecount API를 임의로 구현하지 말 것.

---

## 6. Nine United 포털

| 항목 | 내용 |
|------|------|
| 용도 | 발주 현황, BL 조회 |
| 방식 | 미정 (수동 업로드 or API 검토 중) |
| MVP | **Mock-only** |
| 실 연동 | 별도 승인 필요 |

---

## 7. UNI-PASS 통관

| 항목 | 내용 |
|------|------|
| 용도 | 통관 현황 조회 |
| 방식 | 링크 또는 API (미확정) |
| MVP | **Mock-only** |
| 실 연동 | 별도 승인 필요 |

---

## Adapter 구조 예시

```python
# integrations/github/adapter.py

from abc import ABC, abstractmethod
from dataclasses import dataclass

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

class BaseGithubAdapter(ABC):
    @abstractmethod
    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        ...

class GithubAdapter(BaseGithubAdapter):
    """실제 GitHub API 연동 (Phase 5에서 구현)"""
    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        # 실 구현
        ...

class MockGithubAdapter(BaseGithubAdapter):
    """테스트/개발용 Mock (Phase 1부터 사용)"""
    async def create_issue(self, payload: GithubIssuePayload) -> GithubIssueResult:
        return GithubIssueResult(
            issue_number=9999,
            issue_url="https://github.com/mock/repo/issues/9999",
            state="open"
        )
```
