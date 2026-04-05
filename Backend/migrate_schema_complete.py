"""
Complete database schema migration for external marks system.
This script updates the database to match the new model definitions.
"""

from sqlalchemy import text
from app.core.database import SessionLocal

def migrate_external_marks_table():
    """Migrate external_marks table to new schema"""
    db = SessionLocal()
    try:
        print("\n1. MIGRATING external_marks TABLE...")
        
        # Check if old columns exist
        db.execute(text("SHOW COLUMNS FROM external_marks"))
        existing = db.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'external_marks'"
        )).fetchall()
        existing_cols = [col[0] for col in existing]
        
        # Add new columns if they don't exist
        if 'rollno' not in existing_cols:
            print("   - Adding 'rollno' column...")
            db.execute(text("ALTER TABLE external_marks ADD COLUMN rollno VARCHAR(20)"))
            
        if 'batch' not in existing_cols:
            print("   - Adding 'batch' column...")
            db.execute(text("ALTER TABLE external_marks ADD COLUMN batch VARCHAR(20)"))
            
        if 'branch' not in existing_cols:
            print("   - Adding 'branch' column...")
            db.execute(text("ALTER TABLE external_marks ADD COLUMN branch VARCHAR(20)"))
            
        if 'section' not in existing_cols:
            print("   - Adding 'section' column...")
            db.execute(text("ALTER TABLE external_marks ADD COLUMN section VARCHAR(5)"))
        
        # Remove old gpa column if it exists (we'll calculate it)
        if 'gpa' in existing_cols:
            print("   - Note: 'gpa' column kept for compatibility")
        
        # Remove old grade column if it needs restructuring
        if 'grade' in existing_cols:
            print("   - Note: 'grade' column already exists (can store calculated grade)")
        
        # Also remove external_marks column and make sure we have credits
        if 'external_marks' not in existing_cols:
            print("   - Adding 'external_marks' column for storing marks out of 70...")
            db.execute(text("ALTER TABLE external_marks ADD COLUMN external_marks INT DEFAULT 0"))
        
        db.commit()
        print("   ✓ external_marks table migration completed")
        
    except Exception as e:
        db.rollback()
        print(f"   ✗ Error: {e}")
        raise
    finally:
        db.close()


def migrate_semester_results_table():
    """Migrate semester_results table to new schema"""
    db = SessionLocal()
    try:
        print("\n2. MIGRATING semester_results TABLE...")
        
        # Check if old columns exist
        existing = db.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'semester_results'"
        )).fetchall()
        existing_cols = [col[0] for col in existing]
        
        # Add new columns if they don't exist
        if 'rollno' not in existing_cols:
            print("   - Adding 'rollno' column...")
            db.execute(text("ALTER TABLE semester_results ADD COLUMN rollno VARCHAR(20)"))
            
        if 'batch' not in existing_cols:
            print("   - Adding 'batch' column...")
            db.execute(text("ALTER TABLE semester_results ADD COLUMN batch VARCHAR(20)"))
            
        if 'branch' not in existing_cols:
            print("   - Adding 'branch' column...")
            db.execute(text("ALTER TABLE semester_results ADD COLUMN branch VARCHAR(20)"))
            
        if 'section' not in existing_cols:
            print("   - Adding 'section' column...")
            db.execute(text("ALTER TABLE semester_results ADD COLUMN section VARCHAR(5)"))
            
        if 'cgpa' not in existing_cols:
            print("   - Adding 'cgpa' column (Cumulative GPA)...")
            db.execute(text("ALTER TABLE semester_results ADD COLUMN cgpa FLOAT"))
        
        db.commit()
        print("   ✓ semester_results table migration completed")
        
    except Exception as e:
        db.rollback()
        print(f"   ✗ Error: {e}")
        raise
    finally:
        db.close()


def migrate_internal_marks_table():
    """Migrate internal_marks table to add missing columns"""
    db = SessionLocal()
    try:
        print("\n3. MIGRATING internal_marks TABLE...")
        
        # Check if columns exist
        existing = db.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'internal_marks'"
        )).fetchall()
        existing_cols = [col[0] for col in existing]
        
        # Add missing columns
        if 'objective1' not in existing_cols:
            print("   - Adding 'objective1' column...")
            db.execute(text("ALTER TABLE internal_marks ADD COLUMN objective1 INT"))
            
        if 'objective2' not in existing_cols:
            print("   - Adding 'objective2' column...")
            db.execute(text("ALTER TABLE internal_marks ADD COLUMN objective2 INT"))
            
        if 'mid1' not in existing_cols:
            print("   - Adding 'mid1' column...")
            db.execute(text("ALTER TABLE internal_marks ADD COLUMN mid1 FLOAT"))
            
        if 'mid2' not in existing_cols:
            print("   - Adding 'mid2' column...")
            db.execute(text("ALTER TABLE internal_marks ADD COLUMN mid2 FLOAT"))
        
        db.commit()
        print("   ✓ internal_marks table migration completed")
        
    except Exception as e:
        db.rollback()
        print(f"   ✗ Error: {e}")
        raise
    finally:
        db.close()


def populate_missing_data():
    """Populate new columns with data from existing columns"""
    db = SessionLocal()
    try:
        print("\n4. POPULATING DATA...")
        
        # Copy srno to rollno in external_marks if needed
        db.execute(text("UPDATE external_marks SET rollno = srno WHERE rollno IS NULL"))
        
        # Copy srno to rollno in semester_results if needed
        db.execute(text("UPDATE semester_results SET rollno = srno WHERE rollno IS NULL"))
        
        db.commit()
        print("   ✓ Data population completed")
        
    except Exception as e:
        db.rollback()
        print(f"   ✗ Error: {e}")
        raise
    finally:
        db.close()


def main():
    print("=" * 70)
    print("DATABASE MIGRATION: External Marks & Internal Marks Schema Update")
    print("=" * 70)
    
    try:
        migrate_internal_marks_table()
        migrate_external_marks_table()
        migrate_semester_results_table()
        populate_missing_data()
        
        print("\n" + "=" * 70)
        print("✓ ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Restart the backend server")
        print("2. Test the external marks upload functionality")
        print("\n")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"✗ MIGRATION FAILED: {e}")
        print("=" * 70)
        raise


if __name__ == "__main__":
    main()

