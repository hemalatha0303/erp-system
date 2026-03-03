from pydantic import BaseModel
from typing import List
from datetime import date

class IssueBooksRequest(BaseModel):
    srno: str
    semester: int
    book_codes: List[str]
    issued_date: date
    expected_return_date: date

class ReturnBooksRequest(BaseModel):
    srno: str
    semester: int
    book_codes: List[str]
    return_date: date
    year: int