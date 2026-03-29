#!/usr/bin/env python
"""Check core database tables"""
from sqlalchemy import create_engine, inspect, text
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("=" * 60)
print("DATABASE TABLE INSPECTION")
print("=" * 60)

tables = inspector.get_table_names()
print(f"\nTotal tables in database: {len(tables)}")
print("\nTables found:")
for table in sorted(tables):
    print(f"  - {table}")

print("\n" + "=" * 60)
print("CHECKING CRITICAL TABLES")
print("=" * 60)

critical_tables = ['user', 'student', 'academic', 'faculty', 'payment']
for table in critical_tables:
    if table in tables:
        # Get column count
        columns = inspector.get_columns(table)
        print(f"\n✓ {table.upper()}: {len(columns)} columns")
        for col in columns[:3]:
            print(f"    - {col['name']}: {col['type']}")
        print(f"    ... and {len(columns) - 3} more columns")
    else:
        print(f"\n✗ {table.upper()}: NOT FOUND")

# Try to get row count from student table if it exists
print("\n" + "=" * 60)
if 'student' in tables:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM student"))
            count = result.scalar()
            print(f"\nStudent table row count: {count}")
    except Exception as e:
        print(f"Error checking student table: {e}")
else:
    print("\nStudent table does NOT exist!")

print("\n" + "=" * 60)
