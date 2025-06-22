# scraper/db.py
from fetch.db.sync_engine import engine
from fetch.db.model import Base

def init_db():
    """
    初始化 PostgreSQL 資料庫，建立所有資料表。
    Example db_url: postgresql://user:password@localhost:5432/jobsdb
    """
    Base.metadata.create_all(engine)
    return engine

if __name__ == "__main__":
    init_db()