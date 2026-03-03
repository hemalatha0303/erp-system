from sqlalchemy import text
from app.core.database import engine

def fix_notifications_table():
    with engine.connect() as connection:
        try:
            # Add category column
            print("Adding 'category' column...")
            connection.execute(text("ALTER TABLE notifications ADD COLUMN category VARCHAR(50) DEFAULT 'GENERAL'"))
            
            # Add priority column
            print("Adding 'priority' column...")
            connection.execute(text("ALTER TABLE notifications ADD COLUMN priority VARCHAR(20) DEFAULT 'NORMAL'"))
            
            connection.commit()
            print(" Database updated successfully!")
        except Exception as e:
            print(f" Error (columns might already exist): {e}")

if __name__ == "__main__":
    fix_notifications_table()