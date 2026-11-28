from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import date

from app.api.deps import get_current_user
from app.db.pool import get_pool # Gọi get_pool thay vì get_session
from app.schemas.transaction_schema import TransactionResponse, TransactionCreate, TransactionUpdate
from app.services.transaction_service import TransactionService
from app.repositories.transaction_repo import TransactionRepository

router = APIRouter()

# Tự động lấy và trả kết nối DB từ Pool của Thành viên 1
def get_db_connection():
    pool = get_pool()
    conn = pool.connection()
    try:
        yield conn
    finally:
        conn.close()

def get_transaction_service(conn = Depends(get_db_connection)):
    repo = TransactionRepository(conn)
    return TransactionService(repo)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    return service.create(current_user["id"], data)

@router.get("/")
def get_transactions(
    skip: int = 0, limit: int = 20,
    start_date: Optional[date] = None, end_date: Optional[date] = None,
    min_amount: Optional[float] = None, max_amount: Optional[float] = None,
    category_id: Optional[int] = None, keyword: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    return service.get_list(current_user["id"], skip, limit, start_date, end_date, min_amount, max_amount, category_id, keyword)

@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, current_user: dict = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    return service.get_by_id(current_user["id"], transaction_id)

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, current_user: dict = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    service.delete(current_user["id"], transaction_id)