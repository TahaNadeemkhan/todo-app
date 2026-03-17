from sqlalchemy import create_engine, inspect
from src.config.settings import get_settings

def inspect_table():
    settings = get_settings()
    # Ensure we use a sync driver for inspection
    database_url = settings.database_url.replace('+asyncpg', '')
    print(f"Connecting to: {database_url.split('://')[0]}://***")
    
    engine = create_engine(database_url)
    
    inspector = inspect(engine)
    columns = inspector.get_columns('tasks')
    print("Columns in 'tasks' table:")
    for col in columns:
        print(f"- {col['name']} ({col['type']})")

if __name__ == "__main__":
    inspect_table()
