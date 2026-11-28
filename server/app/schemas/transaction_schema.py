from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Số tiền giao dịch")
    transaction_date: datetime
    note: Optional[str] = None
    transaction_type: TransactionType
    category_id: int
    wallet: str

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    transaction_date: Optional[datetime] = None
    note: Optional[str] = None
    transaction_type: Optional[TransactionType] = None
    category_id: Optional[int] = None
    wallet: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True