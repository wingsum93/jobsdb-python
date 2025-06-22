# scraper/job_repository.py

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from .sync_engine import engine
from fetch.db import Job, JobSnapshot

class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        return self.session.query(Job).get(job_id)

    def create_job(self, job: Job) -> None:
        self.session.add(job)

    def update_job_last_seen(self, job: Job) -> None:
        job.last_seen_at = datetime.utcnow()

    def create_snapshot(self, snapshot: JobSnapshot) -> None:
        self.session.add(snapshot)

    def save_job_and_snapshot(self, job_data: dict, snapshot_data: dict) -> None:
        """
        高層封裝方法：接收 dict（from scraper），自動 upsert job + insert snapshot。
        """
        job = self.get_job_by_id(job_data["job_id"])

        if job is None:
            job = Job(**job_data)
            self.create_job(job)
        else:
            self.update_job_last_seen(job)

        snapshot = JobSnapshot(
            job_id=job.job_id,
            salary=snapshot_data.get("salary"),
            work_type=snapshot_data.get("work_type"),
            employment_type=snapshot_data.get("employment_type"),
            tags=snapshot_data.get("tags"),
            source_url=snapshot_data.get("source_url"),
            raw_html=snapshot_data.get("raw_html"),
        )
        self.create_snapshot(snapshot)

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()
