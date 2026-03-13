# 03 DB SCHEMA STANDARD

## 공통 컬럼 규칙

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID | PK, auto-generate |
| created_at | TIMESTAMPTZ | 생성일시 |
| updated_at | TIMESTAMPTZ | 수정일시 |
| deleted_at | TIMESTAMPTZ nullable | 소프트 삭제 |

## 1. 운영 도메인

### users
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | |
| name | VARCHAR(100) | |
| hashed_password | TEXT | bcrypt |
| role | VARCHAR(50) | UserRole enum |
| is_active | BOOLEAN | default true |
| created_at, updated_at, deleted_at | | |

### projects
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| project_code | VARCHAR(50) UNIQUE | |
| name | VARCHAR(200) | |
| client_name | VARCHAR(200) | |
| service_type | VARCHAR(100) | |
| main_url | VARCHAR(500) | |
| status | ENUM(ProjectStatus) | |
| operation_mode | ENUM(OperationMode) | |
| created_at, updated_at, deleted_at | | |

### project_sites
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| site_code | VARCHAR UNIQUE | |
| site_name | VARCHAR | |
| site_url | VARCHAR | |
| site_type | ENUM(SiteType) | |
| is_enabled | BOOLEAN | |
| created_at, updated_at | | |

### error_reports
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| project_code | VARCHAR INDEX | |
| site_type | ENUM(SiteType) | |
| environment | ENUM(Environment) | |
| app_version | VARCHAR | |
| screen_name | VARCHAR nullable | |
| error_code | VARCHAR INDEX | |
| error_message | TEXT | 원본 |
| error_message_masked | TEXT nullable | 마스킹본 |
| user_context | JSONB nullable | |
| report_status | ENUM(IssueStatus) | default 'new' |
| issue_group_id | UUID FK nullable | |
| trace_id | VARCHAR nullable | |
| occurred_at | TIMESTAMPTZ | |
| created_at | | |

### issue_groups
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| group_key | VARCHAR UNIQUE INDEX | project_code+error_code+screen |
| group_title | VARCHAR | |
| occurrence_count | INTEGER | |
| first_seen_at | TIMESTAMPTZ | |
| last_seen_at | TIMESTAMPTZ | |
| group_status | ENUM(IssueStatus) | |
| github_issue_id | UUID FK nullable | |
| created_at, updated_at | | |

### github_issues
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| issue_group_id | UUID FK | |
| repository | VARCHAR | |
| github_issue_number | INTEGER | |
| github_issue_url | VARCHAR | |
| state | VARCHAR | open/closed |
| created_by | UUID FK nullable | |
| created_at, updated_at | | |

### event_logs
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| project_code | VARCHAR INDEX | |
| environment | ENUM(Environment) | |
| app_version | VARCHAR | |
| event_type | VARCHAR INDEX | |
| event_name | VARCHAR | |
| payload | JSONB nullable | |
| logged_at | TIMESTAMPTZ | |

### admin_actions
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| actor_user_id | UUID FK nullable | |
| action_type | VARCHAR INDEX | |
| target_table | VARCHAR | |
| target_id | UUID nullable | |
| before_data | JSONB nullable | |
| after_data | JSONB nullable | |
| ip_address | VARCHAR nullable | |
| notes | TEXT nullable | |
| created_at | TIMESTAMPTZ | |

### deployment_records
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| project_id | UUID FK | |
| site_id | UUID FK nullable | |
| environment | ENUM(Environment) | |
| version_tag | VARCHAR | |
| deployed_by | UUID FK nullable | |
| deploy_notes | TEXT nullable | |
| deployed_at | TIMESTAMPTZ | |
| status | VARCHAR | success/failed |

### sheet_sync_jobs
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| project_code | VARCHAR | |
| sheet_name | VARCHAR | |
| dataset | VARCHAR | |
| job_type | VARCHAR | export/import |
| job_status | ENUM(SyncJobStatus) | |
| result_url | VARCHAR nullable | |
| error_message | TEXT nullable | |
| idempotency_key | VARCHAR UNIQUE nullable | |
| created_by | UUID FK nullable | |
| created_at, updated_at | | |

## 2. 업무 도메인

### products
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| brand_name | VARCHAR | |
| product_code | VARCHAR UNIQUE | |
| product_name | VARCHAR | |
| category_name | VARCHAR nullable | |
| option_text | VARCHAR nullable | |
| unit_price | NUMERIC(12,4) | |
| currency | VARCHAR(3) | default 'USD' |
| supplier_name | VARCHAR nullable | |
| is_active | BOOLEAN | |
| created_at, updated_at, deleted_at | | |

### inventories
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| product_id | UUID FK UNIQUE | 상품당 1개 |
| warehouse_name | VARCHAR | |
| current_stock | NUMERIC(12,4) | |
| reserved_stock | NUMERIC(12,4) | |
| available_stock | NUMERIC(12,4) | current - reserved |
| safety_stock | NUMERIC(12,4) | |
| expected_inbound_date | DATE nullable | |
| inventory_status | ENUM(InventoryStatus) | |
| created_at, updated_at | | |

### customers
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| customer_type | VARCHAR | individual/business |
| name | VARCHAR | |
| phone | VARCHAR nullable | 원본 암호화 저장 |
| phone_masked | VARCHAR nullable | 표시용 |
| email | VARCHAR nullable | 원본 암호화 저장 |
| email_masked | VARCHAR nullable | 표시용 |
| region | VARCHAR nullable | |
| source_channel | VARCHAR nullable | |
| grade | ENUM(CustomerGrade) | |
| is_vip | BOOLEAN | |
| created_at, updated_at, deleted_at | | |

### contracts
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| contract_number | VARCHAR UNIQUE nullable | CTR-YYYY-MM-SEQ |
| customer_id | UUID FK | |
| consultation_id | UUID FK nullable | |
| contract_date | DATE | |
| contract_amount | NUMERIC(14,2) | |
| deposit_amount | NUMERIC(14,2) nullable | |
| contract_status | ENUM(ContractStatus) | |
| delivery_required | BOOLEAN | |
| remarks | TEXT nullable | |
| created_by | UUID FK nullable | |
| idempotency_key | VARCHAR UNIQUE nullable | |
| created_at, updated_at, deleted_at | | |

### deliveries
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| delivery_number | VARCHAR UNIQUE nullable | DEL-YYYY-MM-SEQ |
| contract_id | UUID FK | |
| customer_id | UUID FK | |
| delivery_date | DATE | |
| time_slot | VARCHAR | 오전/오후/종일 |
| delivery_team | VARCHAR | |
| vehicle_code | VARCHAR nullable | |
| address_text | TEXT | |
| ladder_required | BOOLEAN | |
| delivery_status | ENUM(DeliveryStatus) | |
| idempotency_key | VARCHAR UNIQUE nullable | |
| created_at, updated_at | | |

### capacity_slots
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| slot_date | DATE | |
| delivery_team | VARCHAR | |
| time_slot | VARCHAR | |
| max_capacity | INTEGER | |
| used_capacity | INTEGER | |
| remaining_capacity | INTEGER | |
| slot_status | ENUM(SlotStatus) | |
| UNIQUE(slot_date, delivery_team, time_slot) | | |
| created_at, updated_at | | |
