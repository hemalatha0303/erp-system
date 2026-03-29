from app.models.internal_marks import InternalMarks
from app.models.student import Student
from app.models.academic import Academic
from sqlalchemy import or_, func
from app.utils.marks_calculator import calc_mid_total

def get_internal_marks(db, req):
    student = db.query(Student).filter(
        Student.roll_no == req.roll_no
    ).first()

    if not student:
        raise Exception("Student not found")
    print(req.roll_no, req.subject_name, req.semester)
    query = db.query(InternalMarks).filter(
        InternalMarks.srno == req.roll_no,
        InternalMarks.semester == req.semester
    )
    key = (req.subject_code or req.subject_name or "").strip()
    if key:
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
    mid1 = marks.mid1 if marks.mid1 is not None else calc_mid_total(
        marks.openbook1, marks.objective1, marks.descriptive1, marks.seminar1
    )
    mid2 = marks.mid2 if marks.mid2 is not None else calc_mid_total(
        marks.openbook2, marks.objective2, marks.descriptive2, marks.seminar2
    )
    return {
        "roll_no": req.roll_no,
        "subject_code": marks.subject_code,
        "subject_name": marks.subject_name,
        "year": req.year,
        "semester": req.semester,
        "openbook1": marks.openbook1,
        "openbook2": marks.openbook2,
        "objective1": marks.objective1,
        "objective2": marks.objective2,
        "descriptive1": marks.descriptive1,
        "descriptive2": marks.descriptive2,
        "seminar1": marks.seminar1,
        "seminar2": marks.seminar2,
        "mid1": mid1,
        "mid2": mid2,
    }

def update_internal_marks(db, req):
    key = (req.subject_code or req.subject_name or "").strip()
    query = db.query(InternalMarks).filter(
        InternalMarks.srno == req.roll_no,
        InternalMarks.year == req.year,
        InternalMarks.semester == req.semester
    )
    if key:
        query = query.filter(
            or_(
                InternalMarks.subject_code == key,
                func.lower(InternalMarks.subject_name) == key.lower()
            )
        )

    marks = query.first()

    if not marks:
        student = db.query(Student).filter(Student.roll_no == req.roll_no).first()
        marks = InternalMarks(
            sid=student.id if student else None,
            srno=req.roll_no,
            subject_code=key or req.subject_name,
            subject_name=req.subject_name,
            year=req.year,
            semester=req.semester
        )
        db.add(marks)

    marks.subject_code = key or marks.subject_code
    if req.subject_name:
        marks.subject_name = req.subject_name

    marks.openbook1 = req.openbook1
    marks.openbook2 = req.openbook2
    marks.objective1 = req.objective1
    marks.objective2 = req.objective2
    marks.descriptive1 = req.descriptive1
    marks.descriptive2 = req.descriptive2
    marks.seminar1 = req.seminar1
    marks.seminar2 = req.seminar2
    marks.mid1 = calc_mid_total(req.openbook1, req.objective1, req.descriptive1, req.seminar1)
    marks.mid2 = calc_mid_total(req.openbook2, req.objective2, req.descriptive2, req.seminar2)

    db.commit()
def get_internal_marks_by_student(db, student_roll_no, semester):
    marks = db.query(InternalMarks).filter(
        InternalMarks.srno == student_roll_no,
        InternalMarks.semester == semester
    ).all()
    payload = []
    for m in marks:
        # Use pre-calculated mid values
        mid1 = m.mid1 if m.mid1 is not None else 0
        mid2 = m.mid2 if m.mid2 is not None else 0
        payload.append({
            "subject_code": m.subject_code,
            "subject_name": m.subject_name,
            "objective1": m.objective1,
            "objective2": m.objective2,
            "descriptive1": m.descriptive1,
            "descriptive2": m.descriptive2,
            "openbook1": m.openbook1,
            "openbook2": m.openbook2,
            "seminar1": m.seminar1,
            "seminar2": m.seminar2,
            "mid1": mid1,
            "mid2": mid2,
            "final_internal": m.final_internal_marks
        })

    return {"internal_marks": payload}

