from db import get_session
from fetch.db.model import JobAd

s = get_session()



results = s.query(JobAd).all()
for i, result in enumerate(results):
    print(f"{i+1}. {result.job_title} | {result.company_name} | {result.job_loc} | {result.job_type} | {result.job_post_date} | {result.job_salary_text} | {result.job_description[:80]}...")
    