"""
민감정보 마스킹 유틸리티
저장 전에 반드시 마스킹 처리
"""
import re


def mask_phone(phone: str | None) -> str | None:
    """전화번호 마스킹: 010-1234-5678 → 010-****-5678"""
    if not phone:
        return None
    cleaned = re.sub(r"[^0-9]", "", phone)
    if len(cleaned) == 11:
        return f"{cleaned[:3]}-****-{cleaned[7:]}"
    if len(cleaned) == 10:
        return f"{cleaned[:3]}-***-{cleaned[7:]}"
    return "***-****-****"


def mask_email(email: str | None) -> str | None:
    """이메일 마스킹: user@example.com → u***@example.com"""
    if not email:
        return None
    parts = email.split("@")
    if len(parts) != 2:
        return "***@***.***"
    local = parts[0]
    domain = parts[1]
    if len(local) <= 1:
        return f"{local}***@{domain}"
    return f"{local[0]}***@{domain}"


def mask_error_message(message: str | None) -> str | None:
    """오류 메시지에서 민감정보 제거"""
    if not message:
        return None
    result = message
    result = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL]", result)
    result = re.sub(r"\b01[0-9]-?\d{3,4}-?\d{4}\b", "[PHONE]", result)
    result = re.sub(r"\b\d{6}-?\d{7}\b", "[SSN]", result)
    return result
