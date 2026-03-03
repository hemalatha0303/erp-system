
from openpyxl import load_workbook
from io import BytesIO
from openpyxl import load_workbook
from io import BytesIO
from datetime import datetime
def extract_emails(upload_file):
    
    file_bytes = upload_file.read()
    excel_file = BytesIO(file_bytes)

    wb = load_workbook(excel_file)
    sheet = wb.active

    emails = []
    header = [cell.value for cell in sheet[1]]

    if "email" not in header:
        raise ValueError("Excel must contain 'email' column")

    email_col = header.index("email")

    for row in sheet.iter_rows(min_row=2):
        email = row[email_col].value
        if email:
            emails.append(str(email).strip())

    return emails


def extract_academic_rows(upload_file):
    file_bytes = upload_file.file.read()
    excel = BytesIO(file_bytes)

    wb = load_workbook(excel)
    sheet = wb.active

    header = [cell.value for cell in sheet[1]]
    rows = []

    for row in sheet.iter_rows(min_row=2):
        data = dict(zip(header, [cell.value for cell in row]))

        rows.append({
            "srno": str(data["srno"]),
            "branch": data["branch"],
            "batch": data["batch"],
            "course": data["course"],
            "year": int(data["year"]),
            "semester": int(data["semester"]),
            "section": data["section"],
            "type": data["type"],
            "quota": data.get("quota"),
            "admission_date": data["admission_date"],
            "status": data["status"]
        })

    return rows
