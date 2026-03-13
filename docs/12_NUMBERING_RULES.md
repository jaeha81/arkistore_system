# 12 NUMBERING RULES — 문서번호 생성 규칙

## 1. 계약번호

```
형식: CTR-{YYYY}-{MM}-{SEQUENCE}
예시: CTR-2026-03-0001

규칙:
- YYYY: 연도 4자리
- MM:   월 2자리 (01~12)
- SEQUENCE: 월별 4자리 순번 (0001부터 시작)
- 같은 월 내 순번이 재부여된다 (다음달 0001부터 다시)
```

## 2. 발주 요청번호

```
형식: PRQ-{YYYY}-{MM}-{SEQUENCE}
예시: PRQ-2026-03-0001
```

## 3. 발주서번호

```
형식: PO-{YYYY}-{MM}-{SEQUENCE}
예시: PO-2026-03-0001
```

## 4. 인보이스 내부 관리번호

```
형식: INV-{YYYY}-{MM}-{SEQUENCE}
예시: INV-2026-03-0001

주의: 공급사 인보이스 번호는 invoice_number 필드에 별도 저장
      내부 관리번호와 구분한다
```

## 5. 배송 예약번호

```
형식: DEL-{YYYY}-{MM}-{SEQUENCE}
예시: DEL-2026-03-0001
```

## 6. 번호 생성 규칙

```python
# 서비스 레이어에서 생성
# 예시: contract_service.py

def generate_contract_number(year: int, month: int, sequence: int) -> str:
    return f"CTR-{year:04d}-{month:02d}-{sequence:04d}"

# sequence는 repository에서 SELECT MAX() + 1 또는
# DB sequence 오브젝트로 관리
```

## 7. 번호 중복 방지

- 번호 필드에 UNIQUE 제약 조건 부여
- 생성 시 레이스 컨디션 방지를 위해 DB 레벨 sequence 또는 FOR UPDATE 락 사용
- Idempotency-Key와 별도로 관리
