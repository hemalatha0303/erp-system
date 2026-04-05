"""
Clean up internal_marks table by removing useless columns and adding missing final_internal_marks column
"""
from app.core.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)

# Get current columns
cols = [col["name"] for col in inspector.get_columns("internal_marks")]
print("Current internal_marks columns:", cols)

with engine.connect() as conn:
    # Remove legacy/unexpected columns, keep the canonical schema
    keep_cols = {
        "id",
        "sid",
        "srno",
        "subject_code",
        "subject_name",
        "semester",
        "objective1",
        "descriptive1",
        "openbook1",
        "seminar1",
        "objective2",
        "descriptive2",
        "openbook2",
        "seminar2",
        "mid1",
        "mid2",
        "final_internal_marks",
        "entered_by",
    }

    drop_cols = [col for col in cols if col not in keep_cols]
    for col_name in drop_cols:
        print(f"Removing legacy column: {col_name} ...")
        conn.execute(text(f"ALTER TABLE internal_marks DROP COLUMN {col_name}"))
        print(f"✓ Removed {col_name}")

    # Add final_internal_marks if it doesn't exist
    if "final_internal_marks" not in cols:
        print("Adding final_internal_marks column...")
        conn.execute(text("""
            ALTER TABLE internal_marks 
            ADD COLUMN final_internal_marks FLOAT DEFAULT NULL
        """))
        print("✓ Added final_internal_marks")
    
    conn.commit()

print("\n✅ Database cleanup complete!")
print("\nFinal columns in internal_marks:")
inspector = inspect(engine)
cols = inspector.get_columns("internal_marks")
for col in cols:
    print(f"  - {col['name']}")


