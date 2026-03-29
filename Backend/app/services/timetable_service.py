import os
from app.models.timetable import TimeTable

BASE_PATH = "uploads/timetables"

def upload_timetable_image(
    db, file, year, semester, branch, section, faculty_email, uploaded_by
):
    # Validate inputs
    if not year or not semester or not branch:
        raise ValueError("Year, semester, and branch are required")
    
    # For class timetable: section is required
    if section and not faculty_email:
        folder = f"{BASE_PATH}/students"
        filename = f"{branch}_{year}_{semester}_{section}.png"
    # For faculty workload: faculty_email is required
    elif faculty_email and not section:
        folder = f"{BASE_PATH}/faculty"
        filename = f"{faculty_email}.png"
    else:
        raise ValueError("Either section (for class) or faculty_email (for faculty workload) must be provided, but not both")

    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/{filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    record = TimeTable(
        year=year,
        semester=semester,
        branch=branch,
        section=section,
        faculty_email=faculty_email,
        image_path=file_path,
        uploaded_by=uploaded_by
    )

    db.add(record)
    db.commit()

    return {"message": "Timetable uploaded successfully"}
