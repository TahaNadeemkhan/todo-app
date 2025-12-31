import asyncio
from sqlalchemy import text
from src.db import get_async_session

async def list_users():
    print("Fetching users from database...")
    async for session in get_async_session():
        try:
            # Better Auth uses table "user" (singular, often quoted in Postgres)
            # We'll try to select id, name, email
            result = await session.execute(text('SELECT id, name, email FROM "user" LIMIT 5'))
            users = result.fetchall()
            
            if not users:
                print("\nNo users found in the database!")
                print("Please sign up via the Phase 2 Frontend (http://localhost:3000) to create a user first.")
            else:
                print("\n✅ Found valid users. Use one of these IDs for testing:")
                for u in users:
                    print(f"ID: {u.id} | Name: {u.name} | Email: {u.email}")
        except Exception as e:
            print(f"Error querying users: {e}")

if __name__ == "__main__":
    asyncio.run(list_users())

