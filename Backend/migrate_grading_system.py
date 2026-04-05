"""
Database migration for new grading system tables.
Adds course_grades and semester_grades tables.
"""

from sqlalchemy import text
from app.core.database import SessionLocal

def migrate_grading_tables():
    """Create new grading tables"""
    db = SessionLocal()
    try:
        print("\n" + "="*70)
        print("MIGRATING GRADING SYSTEM TABLES")
        print("="*70)
        
        # Check existing tables
        result = db.execute(text(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE()"
        )).fetchall()
        existing_tables = [row[0] for row in result]
        
        print("\n1. Creating course_grades table...")
        if "course_grades" not in existing_tables:
            db.execute(text("""
                CREATE TABLE course_grades (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    sid INT NOT NULL,
                    srno VARCHAR(20),
                    subject_code VARCHAR(20),
                    subject_name VARCHAR(100),
                    credits INT,
                    internal_marks FLOAT,
                    external_marks FLOAT,
                    semester_marks FLOAT,
                    grade_letter VARCHAR(2),
                    grade_points FLOAT,
                    batch VARCHAR(20),
                    branch VARCHAR(20),
                    section VARCHAR(5),
                    year INT,
                    semester INT,
                    FOREIGN KEY (sid) REFERENCES students(id)
                )
            """))
            print("   ✓ course_grades table created")
        else:
            print("   ℹ course_grades table already exists")
        
        print("\n2. Creating semester_grades table...")
        if "semester_grades" not in existing_tables:
            db.execute(text("""
                CREATE TABLE semester_grades (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    sid INT NOT NULL,
                    srno VARCHAR(20),
                    batch VARCHAR(20),
                    branch VARCHAR(20),
                    section VARCHAR(5),
                    year INT,
                    semester INT,
                    sgpa FLOAT,
                    cgpa FLOAT,
                    cgpa_percentage FLOAT,
                    total_credits INT,
                    result_status VARCHAR(10),
                    FOREIGN KEY (sid) REFERENCES students(id)
                )
            """))
            print("   ✓ semester_grades table created")
        else:
            print("   ℹ semester_grades table already exists")
        
        db.commit()
        print("\n" + "="*70)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        db.close()


def cleanup_old_columns():
    """Remove unnecessary columns from external_marks"""
    db = SessionLocal()
    try:
        print("\n" + "="*70)
        print("CLEANING UP OLD COLUMNS FROM EXTERNAL_MARKS")
        print("="*70 + "\n")
        
        # Check what columns exist
        existing = db.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'external_marks'"
        )).fetchall()
        existing_cols = [col[0] for col in existing]
        
        # Remove unused columns
        columns_to_remove = ['rollno', 'gpa']
        
        for col in columns_to_remove:
            if col in existing_cols:
                print(f"   - Removing column '{col}'...")
                try:
                    db.execute(text(f"ALTER TABLE external_marks DROP COLUMN {col}"))
                except Exception as e:
                    print(f"     (Note: {e})")
        
        db.commit()
        print("\n✓ Cleanup completed\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Cleanup failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_grading_tables()
    cleanup_old_columns()
