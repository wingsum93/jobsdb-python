from sqlalchemy import create_engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session



# 1. Define base model
class Base(DeclarativeBase):
    pass

# 2. Define your table as a Python class
class JobAd(Base):
    __tablename__ = "job_ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jobadid: Mapped[int] = mapped_column(Integer)
    job_title: Mapped[str] = mapped_column(String)
    company_name: Mapped[str] = mapped_column(String)
    job_loc: Mapped[str] = mapped_column(String)
    job_type: Mapped[str] = mapped_column(String)
    job_post_date: Mapped[str] = mapped_column(String)
    job_salary_text: Mapped[str] = mapped_column(String)
    job_description: Mapped[str] = mapped_column(String)


