from app.models.internal_marks import InternalMarks
from app.models.student import Student
from app.models.academic import Academic
from sqlalchemy import or_, func

def get_internal_marks(db, req):
    student = db.query(Student).filter(
        Student.roll_no == req.roll_no
    ).first()

    if not student:
        raise Exception("Student not found")
    print(req.roll_no, req.subject_name, req.year, req.semester)
    query = db.query(InternalMarks).filter(
        InternalMarks.srno == req.roll_no,
        # InternalMarks.subject_code == req.subject_name,
        InternalMarks.year == req.year,
        InternalMarks.semester == req.semester
    )
    if getattr(req, "subject_name", None):
        key = req.subject_name.strip()
        query = query.filter(
            or_(
                InternalMarks.subject_code == key,
                func.lower(InternalMarks.subject_name) == key.lower()
            )
        )
    marks = query.first()
    print(marks, 'subject name')
    if not marks:
        return None
    return {
        "roll_no": req.roll_no,
        "subject_name": req.subject_name,
        "year": req.year,
        "semester": req.semester,
        "subject_name": marks.subject_name,
        "openbook1": marks.openbook1,
        "openbook2": marks.openbook2,
        "descriptive1": marks.descriptive1,
        "descriptive2": marks.descriptive2,
        "seminar1": marks.seminar1,
        "seminar2": marks.seminar2,
        "objective1": marks.objective1,
        "objective2": marks.objective2,
    }

def update_internal_marks(db, req):

    marks = db.query(InternalMarks).filter(
        InternalMarks.srno == req.roll_no,
        InternalMarks.subject_name == req.subject_name,
        InternalMarks.year == req.year,
        InternalMarks.semester == req.semester
    ).first()

    if not marks:
        raise Exception("Internal marks record not found")
    
    marks.openbook1 = req.openbook1
    marks.openbook2 = req.openbook2
    marks.descriptive1 = req.descriptive1
    marks.descriptive2 = req.descriptive2
    marks.seminar1 = req.seminar1
    marks.seminar2 = req.seminar2
    marks.objective1 = req.objective1
    marks.objective2 = req.objective2

    db.commit()
def get_internal_marks_by_student(db, student_roll_no, year, semester):
    

    marks = db.query(InternalMarks).filter(
        InternalMarks.srno == student_roll_no,
        InternalMarks.year == year,
        InternalMarks.semester == semester
    ).all()

    return marks