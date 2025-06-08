from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from model import Base  # ✅ 這邊 import model.py 裡面的 Base
from dotenv import load_dotenv
import os

# ✅ 載入 .env
load_dotenv()
# ✅ 從環境變數讀取
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔌 建立 Engine
engine = create_engine(DATABASE_URL, echo=False)
# 🧠 建立 session factory
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)

# 🏗️ 初始化資料表（只需跑一次）
def init_db():
    Base.metadata.create_all(bind=engine)

# 🧪 Dependency: 取得一個 session
def get_session() -> Session:
    return SessionLocal()









# ----------------------------------
## main entry point
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
# ----------------------------------
# 這段程式碼會建立一個 SQLite 資料庫，並定義一個 `JobAd` 表格。