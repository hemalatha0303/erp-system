#!/usr/bin/env python
"""Test script to verify database tables and columns"""

from app.core.database import SessionLocal, engine
from sqlalchemy import inspect

db = SessionLocal()
inspector = inspect(engine)

print("=" * 60)
print("DATABASE TABLE INSPECTION")
print("=" * 60)

# Check internal_marks table
print("\n1. INTERNAL_MARKS TABLE:")
if "internal_marks" in inspector.get_table_names():
    columns = inspector.get_columns("internal_marks")
    print(f"   ✓ Table exists with {len(columns)} columns:")
    for col in columns:
        print(f"     - {col['name']}: {col['type']}")
else:
    print("   ✗ Table NOT found")

# Check external_marks table
print("\n2. EXTERNAL_MARKS TABLE:")
if "external_marks" in inspector.get_table_names():
    columns = inspector.get_columns("external_marks")
    print(f"   ✓ Table exists with {len(columns)} columns:")
    for col in columns:
        print(f"     - {col['name']}: {col['type']}")
else:
    print("   ✗ Table NOT found")

# Check semester_results table
print("\n3. SEMESTER_RESULTS TABLE:")
if "semester_results" in inspector.get_table_names():
    columns = inspector.get_columns("semester_results")
    print(f"   ✓ Table exists with {len(columns)} columns:")
    for col in columns:
        print(f"     - {col['name']}: {col['type']}")
else:
    print("   ✗ Table NOT found")

print("\n" + "=" * 60)
