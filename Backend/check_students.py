#!/usr/bin/env python
"""Check student data in database"""
from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

print("=" * 60)
print("STUDENT DATA CHECK")
print("=" * 60)

try:
    with engine.connect() as conn:
        # Check student table row count
        result = conn.execute(text("SELECT COUNT(*) FROM students"))
        count = result.scalar()
        print(f"\nTotal students in database: {count}")
        
        if count > 0:
            # Get some sample students
            result = conn.execute(text("""
                SELECT id, roll_no, first_name, last_name, user_email 
                FROM students 
                LIMIT 5
            """))
            print("\nSample students:")
            for row in result:
                print(f"  - Roll: {row[1]}, Name: {row[2]} {row[3]}, Email: {row[4]}")
        else:
            print("\nNo students found in database!")
            print("\nThis means you need to insert student data.")
            print("The student lookup will fail until student records exist.")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
