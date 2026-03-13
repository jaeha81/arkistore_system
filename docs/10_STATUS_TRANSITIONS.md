# 10 STATUS TRANSITIONS

## 1. 계약 상태 전이 (ContractStatus)

```
[draft] ──────────────────────────> [signed]
  │                                    │
  └──> [cancelled]          ┌──────────┘
                             │
                             ▼
                         [confirmed]
                             │
                             └──> [cancelled]
```

| 전이 | 조건 | 담당 |
|------|------|------|
| draft → signed | 계약서 서명 완료 | arki_store_manager |
| signed → confirmed | 입금 확인 완료 | arki_store_manager |
| draft/signed → cancelled | 계약 취소 | arki_store_manager, super_admin |
| confirmed → cancelled | 특별 취소 (메모 필수) | super_admin |

## 2. 발주 요청 상태 전이 (PurchaseRequestStatus)

```
[requested] → [reviewed] → [approved] → [converted_to_order]
                  │
                  └──> [rejected]
```

| 전이 | 조건 | 담당 |
|------|------|------|
| requested → reviewed | 검토 시작 | arki_logistics |
| reviewed → approved | 발주 승인 | arki_logistics |
| reviewed → rejected | 발주 반려 (사유 필수) | arki_logistics |
| approved → converted_to_order | 발주서 생성 완료 시 자동 | system |

## 3. 발주서 상태 전이 (PurchaseOrderStatus)

```
[created] → [ordered] → [invoiced] → [shipped] → [completed]
    │           │            │
    └───────────┴────────────┴──> [cancelled]
```

| 전이 | 조건 | 담당 |
|------|------|------|
| created → ordered | 공급사 주문 발송 완료 | arki_logistics |
| ordered → invoiced | 인보이스 등록 완료 | arki_logistics |
| invoiced → shipped | BL/선적 등록 완료 | arki_logistics |
| shipped → completed | 입고 확인 완료 | arki_logistics |
| any → cancelled | 취소 처리 (사유 필수) | arki_logistics, super_admin |

## 4. 배송 상태 전이 (DeliveryStatus)

```
[scheduled] → [confirmed] → [in_transit] → [completed]
                   │              │
                   └──────────────┴──> [cancelled]
                                  └──> [delayed]
```

| 전이 | 조건 | 담당 |
|------|------|------|
| scheduled → confirmed | 해피콜 완료 후 확정 | arki_store_manager |
| confirmed → in_transit | 배송 출발 | arki_logistics, arki_store_manager |
| in_transit → completed | 배송 완료 확인 | arki_logistics, arki_store_manager |
| in_transit → delayed | 지연 처리 (사유 필수) | arki_logistics, arki_store_manager |
| any → cancelled | 배송 취소 (사유 필수) | arki_store_manager, super_admin |

## 5. 리드 상태 전이 (LeadStatus)

```
[new] → [in_progress] → [converted]
   │           │
   │           └──> [closed]
   └──> [dropped]
```

## 6. 이슈 상태 전이 (IssueStatus)

```
[new] → [grouped] → [triaged] → [github_created] → [resolved]
   │                                                    │
   └──────────────────────────────────────────────> [ignored]
```

## 7. 발주 요청 품목 상태 (PurchaseRequestStatus)

| 상태 | 의미 |
|------|------|
| requested | 요청 대기 |
| reviewed | 검토 중 |
| approved | 승인 완료 |
| rejected | 반려 |
| converted_to_order | 발주서 생성 완료 |

## 8. CAPA 슬롯 상태 (SlotStatus)

| 상태 | 의미 |
|------|------|
| open | 예약 가능 |
| limited | 잔여 50% 이하 |
| full | 잔여 없음 |
| closed | 운영 마감 |
