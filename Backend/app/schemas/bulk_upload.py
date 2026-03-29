from pydantic import BaseModel

class BulkUploadResponse(BaseModel):
    email: str
    password: str
