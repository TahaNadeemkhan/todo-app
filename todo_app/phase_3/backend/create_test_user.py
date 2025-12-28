"""
Create a test user for ChatKit development.
Run this script once to create the test user in the database.
"""
import asyncio
from sqlalchemy import text
from db import get_async_session

async def create_test_user():
    """Create test-user in the database."""
    async for session in get_async_session():
        try:
            # Check if user exists
            result = await session.execute(
                text("SELECT id FROM \"user\" WHERE id = :user_id"),
                {"user_id": "test-user"}
            )
            existing = result.first()

            if existing:
                print("✅ Test user already exists!")
                return

            # Create test user
            await session.execute(
                text("""
                    INSERT INTO "user" (id, email, name, email_verified, created_at, updated_at)
                    VALUES (:id, :email, :name, :email_verified, NOW(), NOW())
                """),
                {
                    "id": "test-user",
                    "email": "test@example.com",
                    "name": "Test User",
                    "email_verified": False
                }
            )
            await session.commit()
            print("✅ Test user created successfully!")
            print("   User ID: test-user")
            print("   Email: test@example.com")

        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            await session.rollback()
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(create_test_user())
