from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


# 1. Define base model
class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)  # e.g. extracted from URL or job element
    title = Column(String, nullable=False)
    company = Column(String)
    location = Column(String)
    detail_url = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_seen_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    snapshots = relationship("JobSnapshot", back_populates="job", cascade="all, delete-orphan")

class JobSnapshot(Base):
    __tablename__ = "job_snapshots"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    snapshot_time = Column(TIMESTAMP, server_default=func.now())
    salary = Column(String)
    work_type = Column(String)
    employment_type = Column(String)
    tags = Column(ARRAY(String))
    source_url = Column(String)
    raw_html = Column(Text)

    job = relationship("Job", back_populates="snapshots")
