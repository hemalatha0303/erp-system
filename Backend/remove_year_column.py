"""
Remove year column from internal_marks table
"""
from app.core.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)
cols = [col["name"] for col in inspector.get_columns("internal_marks")]
print("Current internal_marks columns:", cols)

with engine.connect() as conn:
    if "year" in cols:
        print("Removing year column...")
        conn.execute(text("ALTER TABLE internal_marks DROP COLUMN year"))
        print("✓ Removed year")
    
    conn.commit()

print("\n✅ Column removal complete!")
print("\nFinal columns in internal_marks:")
inspector = inspect(engine)
cols = inspector.get_columns("internal_marks")
for col in cols:
    print(f"  - {col['name']}")
