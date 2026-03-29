"""
Quick verification that all imports and models work
"""
import sys
sys.path.insert(0, 'c:\\Users\\hemal\\Major Project Gallery\\erpProject\\Backend')

try:
    print("Checking imports...")
    from app.models.internal_marks import InternalMarks
    print("✓ InternalMarks model")
    
    from app.models.external_marks import ExternalMarks
    print("✓ ExternalMarks model")
    
    from app.models.course_grade import CourseGrade, SemesterGrade
    print("✓ CourseGrade & SemesterGrade models")
    
    from app.services.excel_marks_service import convert_mark_value
    print("✓ Excel marks service with AB support")
    
    from app.services.faculty_service import get_student_info_by_rollno
    print("✓ Faculty service")
    
    print("\n✅ All imports successful!")
    
    # Test AB conversion
    print("\nTesting AB mark conversion...")
    val, is_absent = convert_mark_value("AB")
    assert val == 0 and is_absent == True, "AB conversion failed"
    print("✓ AB marked as absent: value=0, is_absent=True")
    
    val, is_absent = convert_mark_value(25)
    assert val == 25 and is_absent == False, "Number conversion failed"
    print("✓ Number 25 converted correctly: value=25, is_absent=False")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
