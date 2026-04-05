"""
Drop redundant `year` column from external_marks, course_grades, and semester_grades.
Year of study is implied by semester (e.g. sem 1–2 → year 1).

Run from Backend/:  python migrate_remove_year_grade_tables.py
"""
from sqlalchemy import inspect, text

from app.core.database import engine

TABLES = ("external_marks", "course_grades", "semester_grades")


def main():
    inspector = inspect(engine)
    with engine.connect() as conn:
        for table in TABLES:
            if table not in inspector.get_table_names():
                print(f"Skipping missing table: {table}")
                continue
            cols = [c["name"] for c in inspector.get_columns(table)]
            if "year" not in cols:
                print(f"No year column on {table}")
                continue
            conn.execute(text(f"ALTER TABLE `{table}` DROP COLUMN `year`"))
            print(f"Removed year from {table}")
        conn.commit()
    print("Done.")


if __name__ == "__main__":
    main()
