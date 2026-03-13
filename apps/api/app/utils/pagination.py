"""
페이지네이션 헬퍼
라우터와 서비스에서 공통으로 사용
"""
from dataclasses import dataclass


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def get_pagination(page: int = 1, page_size: int = 20) -> PaginationParams:
    """FastAPI Query 파라미터에서 PaginationParams 생성"""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    return PaginationParams(page=page, page_size=page_size)


def calc_total_pages(total: int, page_size: int) -> int:
    """전체 페이지 수 계산"""
    if total == 0 or page_size == 0:
        return 0
    return (total + page_size - 1) // page_size
