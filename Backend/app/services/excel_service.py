from openpyxl import load_workbook
from io import BytesIO
from datetime import date
from app.models.student import Student
from app.models.academic import Academic
from app.models.payment import Payment
from app.models.fee_structure import FeeStructure

def process_excel(file, db, admin_email):
    file_bytes = BytesIO(file.file.read())
    wb = load_workbook(file_bytes)

    sheet = wb.active

    

    for r in sheet.iter_rows(min_row=2, values_only=True):
        (
            roll, email, fn, ln, gender, residence, mob, pmob,
            branch, batch, course, year, sem, section, quota, adm
        ) = r

        
        student = Student(
            roll_no=roll,
            user_email=email,
            first_name=fn,
            last_name=ln,
            gender=gender,
            residence_type=residence,
            mobile_no=mob,
            parent_mobile_no=pmob
        )
        db.add(student)
        db.flush()

        
        academic = Academic(
            sid=student.id,
            srno=roll,
            user_email=email,
            branch=branch,
            batch=batch,
            course=course,
            year=year,
            semester=sem,
            section=section,
            quota=quota,
            admission_date=adm,
            status="ACTIVE"
        )
        db.add(academic)

        
        fee = db.query(FeeStructure).filter(
            FeeStructure.quota == quota,
            FeeStructure.residence_type == residence,
            FeeStructure.year == year,
            
        ).first()

        if not fee:
            raise Exception(f"Fee structure missing for {roll}")

        
        if fee.tuition_fee > 0:
            db.add(Payment(
                receipt_id=f"INIT-T-{roll}",
                srno=roll,
                student_email=email,
                fee_type="TUITION",
                amount_paid=0,
                year=year,
                semester=sem,
                payment_date=None,
                status="PENDING",
                updated_by=admin_email
            ))

        if residence == "DAY_SCHOLAR":
            db.add(Payment(
                receipt_id=f"INIT-B-{roll}",
                srno=roll,
                student_email=email,
                fee_type="BUS",
                amount_paid=0,
                year=year,
                semester=sem,
                payment_date=date.today(),
                status="PENDING",
                updated_by=admin_email
            ))

        if residence == "HOSTELER":
            db.add(Payment(
                receipt_id=f"INIT-H-{roll}",
                srno=roll,
                student_email=email,
                fee_type="HOSTEL",
                amount_paid=0,
                year=year,
                semester=sem,
                payment_date=date.today(),
                status="PENDING",
                updated_by=admin_email
            ))

    db.commit()
