from typing import Optional
import pymysql
from dbutils.pooled_db import PooledDB
from ..core.config import settings


pool: Optional[PooledDB] = None


def init_db_pool() -> None:
    global pool
    pool = PooledDB(
        creator=pymysql,
        maxconnections=settings.DB_POOL_MAX_SIZE,
        mincached=settings.DB_POOL_MIN_SIZE,
        maxcached=settings.DB_POOL_MAX_SIZE,
        blocking=True,
        ping=1,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset='utf8mb4',
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor
    )


def close_db_pool() -> None:
    global pool
    if pool is not None:
        pool.close()
        pool = None


def get_pool() -> PooledDB:
    if pool is None:
        raise RuntimeError("Database connection pool still not init.")
    return pool