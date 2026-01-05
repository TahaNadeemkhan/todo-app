from sqlmodel import create_engine, text
from todo_app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)

def migrate():
    with engine.connect() as conn:
        print("Migrating tasks table...")
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;"))
            print("Added due_date column")
        except Exception as e:
            print(f"Skipping due_date (probably exists): {e}")
            
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';"))
            print("Added priority column")
        except Exception as e:
            print(f"Skipping priority (probably exists): {e}")
        
        conn.commit()
        print("Migration complete")

if __name__ == "__main__":
    migrate()
