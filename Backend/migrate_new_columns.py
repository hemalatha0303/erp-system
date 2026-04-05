"""
Migration script to add new columns to Student, Faculty, and HOD tables
for the Administration System updates
"""

from sqlalchemy import text, inspect
from app.core.database import engine

def column_exists(table_name, column_name):
    """Check if a column already exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_column(table_name, column_name, column_type):
    """Add a column to a table if it doesn't exist"""
    if column_exists(table_name, column_name):
        print(f"✓ Column '{column_name}' already exists in '{table_name}'")
        return True
    
    try:
        with engine.connect() as connection:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            connection.execute(text(sql))
            connection.commit()
            print(f"✓ Added column '{column_name}' to '{table_name}'")
            return True
    except Exception as e:
        print(f"✗ Error adding '{column_name}' to '{table_name}': {e}")
        return False

def drop_column(table_name, column_name):
    """Drop a column from a table if it exists"""
    if not column_exists(table_name, column_name):
        print(f"✓ Column '{column_name}' does not exist in '{table_name}'")
        return True
    try:
        with engine.connect() as connection:
            sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
            connection.execute(text(sql))
            connection.commit()
            print(f"✓ Dropped column '{column_name}' from '{table_name}'")
            return True
    except Exception as e:
        print(f"✗ Error dropping '{column_name}' from '{table_name}': {e}")
        return False

def _unique_index_exists(table_name, index_name, column_name):
    inspector = inspect(engine)
    for idx in inspector.get_indexes(table_name):
        if idx.get("unique") and (idx.get("name") == index_name or column_name in (idx.get("column_names") or [])):
            return True
    for uc in inspector.get_unique_constraints(table_name):
        if uc.get("name") == index_name or column_name in (uc.get("column_names") or []):
            return True
    return False

def add_unique_index(table_name, column_name, index_name):
    """Add a unique index to a column if it doesn't exist"""
    if _unique_index_exists(table_name, index_name, column_name):
        print(f"✓ Unique index '{index_name}' already exists on '{table_name}'")
        return True
    try:
        with engine.connect() as connection:
            sql = f"CREATE UNIQUE INDEX {index_name} ON {table_name} ({column_name})"
            connection.execute(text(sql))
            connection.commit()
            print(f"✓ Added unique index '{index_name}' on '{table_name}.{column_name}'")
            return True
    except Exception as e:
        print(f"✗ Error adding unique index '{index_name}' on '{table_name}.{column_name}': {e}")
        return False

def migrate_students_table():
    """Add new columns to students table"""
    print("\n=== Updating 'students' table ===")
    columns_to_add = [
        ("personal_email", "VARCHAR(100)"),
        ("branch", "VARCHAR(20)"),
        ("section", "VARCHAR(5)"),
        ("batch", "VARCHAR(20)"),
        ("course", "VARCHAR(20)"),
        ("quota", "VARCHAR(20)"),
        ("admission_date", "DATE"),
    ]
    
    for col_name, col_type in columns_to_add:
        add_column("students", col_name, col_type)

def migrate_faculty_table():
    """Add new columns to faculty table"""
    print("\n=== Updating 'faculty' table ===")
    columns_to_add = [
        ("first_name", "VARCHAR(50)"),
        ("last_name", "VARCHAR(50)"),
        ("mobile_no", "VARCHAR(15)"),
        ("address", "TEXT"),
        ("qualification", "VARCHAR(100)"),
        ("experience", "INT"),
        ("personal_email", "VARCHAR(100)"),
        ("subject_code", "VARCHAR(20)"),
        ("subject_name", "VARCHAR(100)"),
        ("branch", "VARCHAR(20)"),
    ]
    
    for col_name, col_type in columns_to_add:
        add_column("faculty", col_name, col_type)

    columns_to_drop = [
        "gender",
        "blood_group",
        "date_of_birth",
    ]
    for col_name in columns_to_drop:
        drop_column("faculty", col_name)

def migrate_hod_table():
    """Add new columns to hod table"""
    print("\n=== Updating 'hod' table ===")
    columns_to_add = [
        ("personal_email", "VARCHAR(100)"),
        ("first_name", "VARCHAR(100)"),
        ("last_name", "VARCHAR(100)"),
        ("mobile_no", "VARCHAR(15)"),
        ("branch", "VARCHAR(20)"),
        ("address", "TEXT"),
        ("qualification", "VARCHAR(100)"),
        ("experience", "INT"),
    ]
    
    for col_name, col_type in columns_to_add:
        add_column("hod", col_name, col_type)

    columns_to_drop = [
        "name",
        "department",
        "join_date",
    ]
    for col_name in columns_to_drop:
        drop_column("hod", col_name)

def migrate_notifications_table():
    """Add new columns to notifications table"""
    print("\n=== Updating 'notifications' table ===")
    columns_to_add = [
        ("branch", "VARCHAR(20)"),
        ("section", "VARCHAR(5)"),
        ("target_email", "VARCHAR(100)"),
        ("sender_role", "VARCHAR(20)"),
    ]
    for col_name, col_type in columns_to_add:
        add_column("notifications", col_name, col_type)

def migrate_internal_marks_table():
    """Add new columns to internal_marks table"""
    print("\n=== Updating 'internal_marks' table ===")
    columns_to_add = [
        ("objective1", "INT"),
        ("objective2", "INT"),
        ("mid1", "FLOAT"),
        ("mid2", "FLOAT"),
    ]
    for col_name, col_type in columns_to_add:
        add_column("internal_marks", col_name, col_type)

def migrate_external_marks_table():
    """Add new columns to external_marks table"""
    print("\n=== Updating 'external_marks' table ===")
    columns_to_add = [
        ("external_marks", "INT"),
    ]
    for col_name, col_type in columns_to_add:
        add_column("external_marks", col_name, col_type)

def migrate_unique_constraints():
    """Add unique constraints/indexes for key identifiers"""
    print("\n=== Updating unique constraints ===")
    add_unique_index("students", "roll_no", "ux_students_roll_no")
    add_unique_index("users", "email", "ux_users_email")
    add_unique_index("students", "user_email", "ux_students_user_email")
    add_unique_index("faculty", "user_email", "ux_faculty_user_email")
    add_unique_index("hod", "email", "ux_hod_email")

def main():
    """Run all migrations"""
    print("=" * 60)
    print("Database Schema Migration - Administration System Updates")
    print("=" * 60)
    
    try:
        # Check database connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("\n✓ Database connection successful")
        
        # Run migrations
        migrate_students_table()
        migrate_faculty_table()
        migrate_hod_table()
        migrate_notifications_table()
        migrate_internal_marks_table()
        migrate_external_marks_table()
        migrate_unique_constraints()
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

