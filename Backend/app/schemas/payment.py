from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any


class StudentPaymentLookupResponse(BaseModel):
    srno: str
    name: str
    branch: str
    year: int
    email: str


class PaymentCreateRequest(BaseModel):
    receipt_id: str
    fee_type: str
    amount_paid: float
    payment_mode: str
    status: str
    year: int
    semester: int
    payment_date: date


class PaymentUpdateRequest(BaseModel):
    roll_no: str
    fee_type: str        
    amount: float
    payment_mode: str
    payment_details: Optional[Dict[str, Any]] = None


class StudentPaymentSubmitRequest(BaseModel):
    fee_type: str
    amount: float
    payment_mode: str
    payment_details: Optional[Dict[str, Any]] = None


    