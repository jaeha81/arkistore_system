import asyncio
import uuid

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.capacity_slot import CapacitySlot
from app.models.product import Product
from app.models.user import User


INITIAL_USERS = [
    {
        "email": "admin@arkistore.com",
        "name": "슈퍼관리자",
        "password": "Admin1234!",
        "role": "super_admin",
    },
    {
        "email": "ops@arkistore.com",
        "name": "운영관리자",
        "password": "Ops12345!",
        "role": "ops_admin",
    },
    {
        "email": "logistics@arkistore.com",
        "name": "물류담당자",
        "password": "Arki1234!",
        "role": "arki_logistics",
    },
    {
        "email": "sales@arkistore.com",
        "name": "영업담당자",
        "password": "Arki1234!",
        "role": "arki_sales",
    },
    {
        "email": "manager@arkistore.com",
        "name": "판매매니저",
        "password": "Arki1234!",
        "role": "arki_store_manager",
    },
]

SAMPLE_PRODUCTS = [
    {
        "brand_name": "샘플브랜드A",
        "product_code": "PRD-001",
        "product_name": "소파 3인용 그레이",
        "category_name": "소파",
        "unit_price": 850000,
        "currency": "KRW",
        "supplier_name": "공급사A",
    },
    {
        "brand_name": "샘플브랜드B",
        "product_code": "PRD-002",
        "product_name": "식탁 4인용 화이트",
        "category_name": "식탁",
        "unit_price": 620000,
        "currency": "KRW",
        "supplier_name": "공급사B",
    },
    {
        "brand_name": "샘플브랜드A",
        "product_code": "PRD-003",
        "product_name": "침대 퀸사이즈 베이지",
        "category_name": "침대",
        "unit_price": 1200000,
        "currency": "KRW",
        "supplier_name": "공급사A",
    },
]


async def seed_users(db) -> None:
    print("\n[1/3] 사용자 계정 생성 중...")
    for u in INITIAL_USERS:
        exists = await db.execute(
            __import__("sqlalchemy").select(User).where(User.email == u["email"])
        )
        if exists.scalar_one_or_none():
            print(f"  SKIP (이미 존재): {u['email']}")
            continue

        user = User(
            id=uuid.uuid4(),
            email=u["email"],
            name=u["name"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
            is_active=True,
        )
        db.add(user)
        print(f"  CREATE: {u['email']} / {u['password']} ({u['role']})")

    await db.commit()


async def seed_products(db) -> None:
    from sqlalchemy import select
    print("\n[2/3] 샘플 제품 생성 중...")
    for p in SAMPLE_PRODUCTS:
        exists = await db.execute(
            select(Product).where(Product.product_code == p["product_code"])
        )
        if exists.scalar_one_or_none():
            print(f"  SKIP (이미 존재): {p['product_code']}")
            continue

        product = Product(
            id=uuid.uuid4(),
            **p,
            is_active=True,
        )
        db.add(product)
        print(f"  CREATE: {p['product_code']} - {p['product_name']}")

    await db.commit()


async def seed_capacity_slots(db) -> None:
    from sqlalchemy import select
    from datetime import date, timedelta
    print("\n[3/3] 배송 CAPA 슬롯 생성 중 (오늘 ~ 30일)...")

    teams = ["A팀", "B팀"]
    time_slots = ["오전(09-12)", "오후(13-17)", "야간(18-21)"]
    today = date.today()
    count = 0

    for i in range(30):
        slot_date = today + timedelta(days=i)
        for team in teams:
            for time_slot in time_slots:
                exists = await db.execute(
                    select(CapacitySlot).where(
                        CapacitySlot.slot_date == slot_date,
                        CapacitySlot.delivery_team == team,
                        CapacitySlot.time_slot == time_slot,
                    )
                )
                if exists.scalar_one_or_none():
                    continue

                slot = CapacitySlot(
                    id=uuid.uuid4(),
                    slot_date=slot_date,
                    delivery_team=team,
                    time_slot=time_slot,
                    max_capacity=5,
                    used_capacity=0,
                    remaining_capacity=5,
                    slot_status="open",
                )
                db.add(slot)
                count += 1

    await db.commit()
    print(f"  CREATE: {count}개 슬롯 생성 완료")


async def main():
    print("=" * 50)
    print("Arkistore 초기 데이터 시드")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        await seed_users(db)
        await seed_products(db)
        await seed_capacity_slots(db)

    print("\n✅ 시드 완료!")
    print("\n[계정 정보]")
    for u in INITIAL_USERS:
        print(f"  {u['role']:25s} | {u['email']:30s} | {u['password']}")


if __name__ == "__main__":
    asyncio.run(main())
