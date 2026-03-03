from pydantic import BaseModel
from typing import List

class FeeStructureCreate(BaseModel):
    quota: str                 
    residence_type: str        
    tuition_fee: float
    bus_fee: float
    hostel_fee: float
    year: int
    


class FeeStructureBulkCreate(BaseModel):
    items: List[FeeStructureCreate]
