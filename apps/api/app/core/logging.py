"""
애플리케이션 로깅 설정
구조화된 JSON 로깅 지원
"""
import logging
import sys
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """로깅 초기화 - main.py 시작 시 호출"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # 외부 라이브러리 노이즈 억제
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거 반환"""
    return logging.getLogger(name)


class AuditLogger:
    """
    감사 이벤트 전용 로거
    구조화된 형식으로 기록
    """

    _logger = logging.getLogger("audit")

    @classmethod
    def log(
        cls,
        action_type: str,
        actor_id: str | None,
        target_table: str,
        target_id: str | None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        record = {
            "action": action_type,
            "actor": actor_id,
            "table": target_table,
            "target": target_id,
        }
        if extra:
            record.update(extra)
        cls._logger.info("AUDIT | %s", record)
