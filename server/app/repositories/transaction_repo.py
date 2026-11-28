from typing import Optional, List
from datetime import date
from app.schemas.transaction_schema import TransactionCreate, TransactionUpdate

class TransactionRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_transaction(self, user_id: int, data: TransactionCreate) -> dict:
        with self.conn.cursor() as cursor:
            sql = """
                INSERT INTO transactions (user_id, category_id, amount, type, transaction_date, note, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Ánh xạ từ schema sang cột trong table
            cursor.execute(sql, (
                user_id, data.category_id, data.amount, data.transaction_type.value,
                data.transaction_date, data.note, data.wallet
            ))
            self.conn.commit()
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (cursor.lastrowid,))
            return cursor.fetchone()

    def get_transaction_by_id(self, user_id: int, transaction_id: int) -> Optional[dict]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM transactions WHERE id = %s AND user_id = %s", (transaction_id, user_id))
            return cursor.fetchone()

    def get_transactions(
        self, user_id: int, skip: int = 0, limit: int = 20,
        start_date: Optional[date] = None, end_date: Optional[date] = None,
        min_amount: Optional[float] = None, max_amount: Optional[float] = None,
        category_id: Optional[int] = None, keyword: Optional[str] = None
    ) -> List[dict]:
        with self.conn.cursor() as cursor:
            query = "SELECT * FROM transactions WHERE user_id = %s"
            params = [user_id]

            if start_date:
                query += " AND transaction_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND transaction_date <= %s"
                params.append(end_date)
            if min_amount is not None:
                query += " AND amount >= %s"
                params.append(min_amount)
            if max_amount is not None:
                query += " AND amount <= %s"
                params.append(max_amount)
            if category_id:
                query += " AND category_id = %s"
                params.append(category_id)
            if keyword:
                query += " AND note LIKE %s"
                params.append(f"%{keyword}%")

            query += " LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    def delete_transaction(self, user_id: int, transaction_id: int) -> bool:
        with self.conn.cursor() as cursor:
            affected = cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (transaction_id, user_id))
            self.conn.commit()
            return affected > 0