from playwright.sync_api import sync_playwright
from fetch.selector import PostSelector, ListSelector
from urllib.parse import urlparse, parse_qs
import json
import os
import time
import random
from dataclasses import dataclass
from fetch.db.job_repository import JobRepository
from fetch import SessionLocal

@dataclass
class ScrapedJobData:
    job_id: int
    title: str
    company: str
    location: str
    detail_url: str
    description: str
    requirements: str
    salary: str
    work_type: str
    employment_type: str
    tags: list[str]
    source_url: str
    raw_html: str


class JobsDBScraper:
    def __init__(self, start_url: str,session:any, headless: bool = False):
        self.start_url = start_url
        self.headless = headless
        self.session = session
        self.job_repo = JobRepository(self.session)
        self.total_jobs_extracted = 0

    def load_cookies(self, page, filename="cookies.json"):
        temp_dir = os.path.join(os.getcwd(), "temp")
        file_path = os.path.join(temp_dir, filename)
        if not os.path.exists(file_path):
            print(f"[✘] 找不到 cookie 檔案：{file_path}")
            return
        with open(file_path, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                page.context.add_cookies([cookie])
        page.reload()

    def have_next_page(self, page):
        try:
            next_button = page.query_selector(ListSelector.NEXT_PAGE_BTN)
            if next_button and next_button.is_visible():
                aria_hidden = next_button.get_attribute("aria-hidden")
                return aria_hidden != "true"
            return False
        except Exception as e:
            print(f"❌ Error checking for next page: {e}")
            return False

    def go_to_next_page(self, page):
        try:
            next_button = page.query_selector(ListSelector.NEXT_PAGE_BTN)
            if next_button:
                next_button.click()
                page.wait_for_selector(ListSelector.JOB)
        except Exception as e:
            print(f"❌ Error going to next page: {e}")

    def get_job_salary(self, page):
        try:
            job_detail_salary = page.query_selector(PostSelector.DETAIL_SALARY)
            return job_detail_salary.inner_text()
        except Exception:
            job_expected_salary = page.query_selector(PostSelector.EXPECTED_SALARY)
            return job_expected_salary.inner_text() if job_expected_salary else ""

    def extract_job(self, page):
        try:
            job_title = page.query_selector(PostSelector.TITLE).inner_text()
            company_name = page.query_selector(PostSelector.COMPANY_NAME).inner_text()
            job_loc = page.query_selector(PostSelector.LOCATION).inner_text()
            job_type = page.query_selector(PostSelector.WORK_TYPE).inner_text()
            job_salary_text = self.get_job_salary(page)
            job_des = page.query_selector(PostSelector.DESCRIPTION).inner_text()
            url = page.url
            job_id = int(parse_qs(urlparse(url).query).get("jobId", [-1])[0])

            return ScrapedJobData(
                job_id=job_id,
                title=job_title,
                company=company_name,
                location=job_loc,
                detail_url=url,
                description=job_des,
                requirements="",
                salary=job_salary_text,
                work_type=job_type,
                employment_type="",
                tags=[],
                source_url=url,
                raw_html=page.content()
            )
        except Exception as e:
            print(f"❌ Failed to extract job: {e}")
            return None

    def loop_through_one_page(self, page):
        elements = page.query_selector_all(ListSelector.JOB)
        print(f"Found {len(elements)} elements.")
        no_of_success = 0
        for idx, element in enumerate(elements):
            try:
                element.scroll_into_view_if_needed()
                element.click()
                page.wait_for_selector(PostSelector.TITLE, timeout=10000)
                job_ad = self.extract_job(page)
                if job_ad:
                    self.job_repo.save_job_and_snapshot(
                        job_data={
                            "job_id": str(job_ad.job_id),
                            "title": job_ad.title,
                            "company": job_ad.company,
                            "location": job_ad.location,
                            "detail_url": job_ad.detail_url,
                            "description": job_ad.description,
                            "requirements": job_ad.requirements,
                        },
                        snapshot_data={
                            "salary": job_ad.salary,
                            "work_type": job_ad.work_type,
                            "employment_type": job_ad.employment_type,
                            "tags": job_ad.tags,
                            "source_url": job_ad.source_url,
                            "raw_html": job_ad.raw_html,
                        }
                    )
                    no_of_success += 1
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"[{idx + 1}] Click failed: {e}")

        self.job_repo.commit()
        return no_of_success

    def run(self, load_cookie=False):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.goto(self.start_url)

            if load_cookie:
                self.load_cookies(page)

            page.wait_for_timeout(5000)
            current_page_number = 1

            no_of_success = self.loop_through_one_page(page)
            self.total_jobs_extracted += no_of_success

            while self.have_next_page(page):
                self.go_to_next_page(page)
                current_page_number += 1
                print(f"Processing page {current_page_number}...")
                no_of_success = self.loop_through_one_page(page)
                print(f"Page {current_page_number} processed with {no_of_success} successful job ads.")
                self.total_jobs_extracted += no_of_success

            print(f"Total number of jobs extracted: {self.total_jobs_extracted}")
            browser.close()
            self.session.close()


def main():
    scraper = JobsDBScraper(
        start_url="https://hk.jobsdb.com/android-jobs?page=1",
        session=SessionLocal(),
        headless=False
    )
    scraper.run(load_cookie=False)


if __name__ == "__main__":
    main()
