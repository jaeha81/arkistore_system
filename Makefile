.PHONY: help api-install api-run api-test api-migrate ops-run arki-run

help:
	@echo "Arkistore Operations Automation System"
	@echo ""
	@echo "Usage:"
	@echo "  make api-install    백엔드 의존성 설치"
	@echo "  make api-run        백엔드 개발 서버 실행"
	@echo "  make api-test       백엔드 테스트 실행"
	@echo "  make api-migrate    DB 마이그레이션 실행"
	@echo "  make ops-run        ops-web 개발 서버 실행"
	@echo "  make arki-run       arki-web 개발 서버 실행"

api-install:
	cd apps/api && pip install -e ".[dev]"

api-run:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-test:
	cd apps/api && pytest tests/ -v

api-migrate:
	cd apps/api && alembic upgrade head

api-migrate-create:
	cd apps/api && alembic revision --autogenerate -m "$(msg)"

ops-install:
	cd apps/ops-web && npm install

ops-run:
	cd apps/ops-web && npm run dev

arki-install:
	cd apps/arki-web && npm install

arki-run:
	cd apps/arki-web && npm run dev

install-all:
	make api-install && make ops-install && make arki-install
