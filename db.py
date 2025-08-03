from databases import Database
import asyncio

DATABASE_URL = "mysql+asyncmy://root:Petuxovyar2006_@localhost:3306/todo"


async def get_connection():
    db = Database("mysql+asyncmy://root:password@localhost:3306/testdb")
    await db.connect()
    try:
        result = await db.fetch_one("SELECT 1")
        print("Success:", result)
    finally:
        await db.disconnect()