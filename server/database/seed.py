import os
import pandas as pd
import pymysql
from passlib.context import CryptContext
from dotenv import load_dotenv
from ..app.core.security import hash_password
from ..app.core.config import settings

load_dotenv()
DB_CONFIG = {
    "host": settings.DB_HOST,
    "port": int(settings.DB_PORT),
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "database": settings.DB_NAME,
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor 
}

DEFAULT_PASSWORD = hash_password("123456")

def seed_from_csv(csv_path: str = "personal_finance_tracker_dataset.csv"):
    print(f"Reading data from {csv_path}")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])

    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cursor:
            cursor.execute("select id, name, type from categories where user_id is null")
            categories = cursor.fetchall()
            cat_map = {(c["name"], c["type"]): c['id'] for c in categories}

            if not cat_map:
                raise RuntimeError("Categories not defined. Run file schema.sql first.")

            unique_users = sorted(df["user_id"].unique().tolist())
            user_rows = [
                (int(uid), f"user{uid}@example.com", DEFAULT_PASSWORD, f"User {uid} ")
                for uid in unique_users
            ]
            cursor.executemany(
                """
                INSERT IGNORE INTO users (id, email, hashed_password, full_name)
                VALUES (%s, %s, %s, %s)
""", user_rows
            )
            print(f"Inserted {len(user_rows)} users. (Default password: 123456)")

            tx_rows = []
            budget_rows = []
            snapshot_rows = []

            for _, row in df.iterrows():
                uid = int(row["user_id"])
                dt = row["date"]
                dt_str = dt.strftime("%Y-%m-%d 00:00:00")
                date_only = dt.strftime("%Y-%m-%d")

                inc_cat_id = cat_map.get((row["income_type"], "INCOME"))

                tx_rows.append((
                    uid,
                    inc_cat_id,
                    float(row["monthly_income"]),
                    "INCOME",
                    dt_str,
                    f"Income Source {row['income_type']} ({row['financial_scenario']})",
                    "BANK_TRANSFER"
                ))

                exp_cat_id = cat_map.get((row["category"], "EXPENSE"))

                tx_rows.append((
                    uid,
                    exp_cat_id,
                    float(row["monthly_expense_total"]),
                    "EXPENSE",
                    dt_str,
                    f"Expense {row['category']} (Transactions: {row['financial_scenario']})",
                    "BANK_TRANSFER"
                ))

                budget_rows.append((
                    uid,
                    None,
                    float(row["budget_goal"]),
                    int(dt.month),
                    int(dt.year)
                ))

                snapshot_rows.append((
                    uid,
                    date_only,
                    float(row["monthly_income"]),
                    float(row["monthly_expense_total"]),
                    float(row["actual_savings"]),
                    float(row["savings_rate"]),
                    float(row["essential_spending"]),
                    float(row["discretionary_spending"]),
                    float(row["credit_score"]),
                    float(row["debt_to_income_ratio"]),
                    float(row["emergency_fund"]),
                    str(row["financial_scenario"]),
                    str(row["cash_flow_status"]),
                    str(row["financial_stress_level"]),
                ))

            cursor.executemany(
                """
                INSERT INTO transactions (user_id, category_id, amount, type, transaction_date, note, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                tx_rows,
            )
            print(f"Inserted {len(tx_rows)} transactions (Income & Expense).")

            # Batch Insert Budgets (cập nhật nếu trùng user + tháng + năm)
            cursor.executemany(
                """
                INSERT INTO budgets (user_id, category_id, amount_limit, month, year)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE amount_limit = VALUES(amount_limit)
                """,
                budget_rows,
            )
            print(f"Inserted {len(budget_rows)} budgets.")

            # Batch Insert Financial Snapshots
            cursor.executemany(
                """
                INSERT INTO financial_snapshots (
                    user_id, record_date, monthly_income, monthly_expense_total,
                    actual_savings, savings_rate, essential_spending, discretionary_spending,
                    credit_score, debt_to_income_ratio, emergency_fund,
                    financial_scenario, cash_flow_status, financial_stress_level
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                snapshot_rows,
            )
            print(f"Inserted {len(snapshot_rows)} financial_snapshots.")

        conn.commit()
        print("Seed data successfull!")
  
    except Exception as e:
        conn.rollback()
        print(f"Error while seeding data, Rollbacked:", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_from_csv()