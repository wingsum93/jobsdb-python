
import csv
from fetch.db.model import JobAd
from db import get_session  # 你 db.py 裡面的 session 建立方法

def export_job_ads_to_csv(filename: str = "job_ads.csv"):
    session = get_session()

    # 查詢全部 JobAd 資料
    job_ads = session.query(JobAd).all()

    # 開啟 CSV 檔案
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # 寫入標頭
        writer.writerow([
            "id", "jobadid", "job_title", "company_name", "job_loc",
            "job_type", "job_post_date", "job_salary_text", "job_description"
        ])

        # 寫入每一列資料
        for job in job_ads:
            writer.writerow([
                job.id,
                job.jobadid,
                job.job_title,
                job.company_name,
                job.job_loc,
                job.job_type,
                job.job_post_date,
                job.job_salary_text,
                job.job_description.replace("\n", " ").strip()  # 可選：清理換行
            ])

    print(f"✅ Exported {len(job_ads)} job ads to {filename}")
if __name__ == "__main__":
    export_job_ads_to_csv("output_jobs.csv")