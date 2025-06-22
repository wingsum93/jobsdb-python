from playwright.sync_api import sync_playwright
from fetch.selector import PostSelector, ListSelector
from urllib.parse import urlparse, parse_qs
from fetch.db import Job, JobSnapshot
from fetch.db import insert_all_job_ads
import json
import os
import time
import random



def load_cookies(page, filename="cookies.json"):
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


def have_next_page(page):
    try:
        next_button = page.query_selector(ListSelector.NEXT_PAGE_BTN)
        if next_button and next_button.is_visible():
            aria_hidden = next_button.get_attribute("aria-hidden")
            return aria_hidden != "true"
        return False
    except Exception as e:
        print(f"❌ Error checking for next page: {e}")
        return False


def go_to_next_page(page):
    try:
        next_button = page.query_selector(ListSelector.NEXT_PAGE_BTN)
        if next_button:
            next_button.click()
            page.wait_for_selector(ListSelector.JOB)
    except Exception as e:
        print(f"❌ Error going to next page: {e}")


def get_job_salary(page):
    try:
        job_detail_salary = page.query_selector(PostSelector.DETAIL_SALARY)
        return job_detail_salary.inner_text()
    except Exception:
        job_expected_salary = page.query_selector(PostSelector.EXPECTED_SALARY)
        return job_expected_salary.inner_text() if job_expected_salary else ""


def extract_job(page):
    try:
        job_title = page.query_selector(PostSelector.TITLE).inner_text()
        company_name = page.query_selector(PostSelector.COMPANY_NAME).inner_text()
        job_loc = page.query_selector(PostSelector.LOCATION).inner_text()
        job_type = page.query_selector(PostSelector.WORK_TYPE).inner_text()
        job_salary_text = get_job_salary(page)
        job_des = page.query_selector(PostSelector.DESCRIPTION).inner_text()
        url = page.url
        job_id = int(parse_qs(urlparse(url).query).get("jobId", [-1])[0])

        return JobAd(
            jobadid=job_id,
            job_title=job_title,
            company_name=company_name,
            job_loc=job_loc,
            job_type=job_type,
            job_post_date="",
            job_salary_text=job_salary_text,
            job_description=job_des
        )
    except Exception as e:
        print(f"❌ Failed to extract job: {e}")
        return None


def loop_through_one_page(page):
    elements = page.query_selector_all(ListSelector.JOB)
    print(f"Found {len(elements)} elements.")
    job_ads = []

    for idx, element in enumerate(elements):
        try:
            element.scroll_into_view_if_needed()
            element.click()
            page.wait_for_selector(PostSelector.TITLE, timeout=10000)
            job_ad = extract_job(page)
            if job_ad:
                job_ads.append(job_ad)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"[{idx + 1}] Click failed: {e}")

    insert_all_job_ads(job_ads)
    return len(job_ads)


def main(load_cookie=False):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://hk.jobsdb.com/android-jobs?page=1")
        if load_cookie:
            load_cookies(page)

        page.wait_for_timeout(5000)

        current_page_number = 1
        total_number_of_jobs_extracted = 0

        noOfSuccess = loop_through_one_page(page)
        total_number_of_jobs_extracted += noOfSuccess

        while have_next_page(page):
            go_to_next_page(page)
            current_page_number += 1
            print(f"Processing page {current_page_number}...")
            noOfSuccess = loop_through_one_page(page)
            print(f"Page {current_page_number} processed with {noOfSuccess} successful job ads.")
            total_number_of_jobs_extracted += noOfSuccess

        print(f"Total number of jobs extracted: {total_number_of_jobs_extracted}")
        browser.close()


if __name__ == "__main__":
    main()
