from pydantic import BaseModel

class ExcelUploadResponse(BaseModel):
    message: str
