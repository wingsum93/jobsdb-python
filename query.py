from db import get_session
from model import JobAd
from sqlalchemy.orm import Session


s = get_session()



results = s.query(JobAd).all()
for i, result in enumerate(results):
    print(f"{i+1}. {result.job_title} | {result.company_name} | {result.job_loc} | {result.job_type} | {result.job_post_date} | {result.job_salary_text} | {result.job_description[:80]}...")
    