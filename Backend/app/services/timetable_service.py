import os
from app.models.timetable import TimeTable

BASE_PATH = "uploads/timetables"

def upload_timetable_image(
    db, file, year, semester, branch, section, faculty_email, uploaded_by
):
    if section:
        folder = f"{BASE_PATH}/students"
        filename = f"{branch}_{year}_{semester}_{section}.png"
    else:
        folder = f"{BASE_PATH}/faculty"
        filename = f"{faculty_email}.png"

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
