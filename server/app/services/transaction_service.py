from typing import Optional, List
from datetime import date
from fastapi import HTTPException, status
from app.schemas.transaction_schema import TransactionCreate, TransactionUpdate
from app.repositories.transaction_repo import TransactionRepository

class TransactionService:
    def __init__(self, repo: TransactionRepository):
        self.repo = repo

    def create(self, user_id: int, data: TransactionCreate):
        return self.repo.create_transaction(user_id, data)

    def get_by_id(self, user_id: int, transaction_id: int):
        transaction = self.repo.get_transaction_by_id(user_id, transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
        return transaction

    def get_list(self, user_id: int, skip: int, limit: int, start_date: Optional[date], end_date: Optional[date], min_amount: Optional[float], max_amount: Optional[float], category_id: Optional[int], keyword: Optional[str]):
        return self.repo.get_transactions(user_id, skip, limit, start_date, end_date, min_amount, max_amount, category_id, keyword)

    def delete(self, user_id: int, transaction_id: int):
        success = self.repo.delete_transaction(user_id, transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
        return success