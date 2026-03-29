from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)

# Get external_marks columns
print('=== EXTERNAL_MARKS TABLE ===')
if 'external_marks' in inspector.get_table_names():
    cols = inspector.get_columns('external_marks')
    for col in cols:
        print(f'{col["name"]}: {col["type"]}')
else:
    print('TABLE NOT FOUND')

print('\n=== INTERNAL_MARKS TABLE ===')
if 'internal_marks' in inspector.get_table_names():
    cols = inspector.get_columns('internal_marks')
    for col in cols:
        print(f'{col["name"]}: {col["type"]}')
else:
    print('TABLE NOT FOUND')

print('\n=== COURSE_GRADES TABLE ===')
if 'course_grades' in inspector.get_table_names():
    print('EXISTS')
    cols = inspector.get_columns('course_grades')
    for col in cols:
        print(f'  {col["name"]}')
else:
    print('NOT FOUND - NEEDS CREATION')

print('\n=== SEMESTER_GRADES TABLE ===')
if 'semester_grades' in inspector.get_table_names():
    print('EXISTS')
    cols = inspector.get_columns('semester_grades')
    for col in cols:
        print(f'  {col["name"]}')
else:
    print('NOT FOUND - NEEDS CREATION')
