from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from model import JobAd
from db import get_session
from db import insert_all_job_ads
import time
import csv
import json


def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# ----------------------------------
### container for outer conteainer 
### div block _1oozmqe0 l218ib5b l218ibhf l218ib6v


### tried job selectors
### div._1oozmqe0.l218ib4v.l218ib51 a[data-automation="job-list-item-link-overlay"]
### a[data-automation="jobTitle"]

job_selector = 'a[data-automation="jobTitle"]'
job_title_selector = 'h1[data-automation="job-detail-title"]'
job_company_name_selector = 'span[data-automation="advertiser-name"]'
job_location_selector = 'span[data-automation="job-detail-location"]'
job_work_type_selector = 'span[data-automation="job-detail-work-type"]'
job_detail_salary_selector = 'span[data-automation="job-detail-salary"]'
job_expected_salary_selector = 'span[data-automation="job-detail-add-expected-salary"]'
job_post_date_selector = 'span._1oozmqe0.l218ib4z._1ljn1h70._1ljn1h71._1ljn1h71u._1ljn1h76._1kdtdvw4'
job_description_selector = 'div[data-automation="jobAdDetails"'

next_page_button_selector = 'li._1oozmqe0.l218ibbb.l218ibb0.l218ibx a' # Next page button selector
total_job_number_count_selector = 'span[data-automation="totalJobsCount"]'

def have_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, next_page_button_selector)
        return next_button.get('aria-hidden') != 'true'
    except Exception as e:
        print(f"❌ Error checking for next page: {e}")
        return False
    
def go_to_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, next_page_button_selector)
        next_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, job_selector))
        )
    except Exception as e:
        print(f"❌ Error going to next page: {e}")

def get_job_salary(driver):
    try:
        job_detail_salary = driver.find_element(By.CSS_SELECTOR,job_detail_salary_selector)
        return job_detail_salary.text
    except Exception as e:
        job_expected_salary = driver.find_element(By.CSS_SELECTOR,job_expected_salary_selector)
        return job_expected_salary.text
def extract_job(driver):
    try:
        job_title = driver.find_element(By.CSS_SELECTOR, job_title_selector).text
        company_name = driver.find_element(By.CSS_SELECTOR, job_company_name_selector).text
        job_loc = driver.find_element(By.CSS_SELECTOR, job_location_selector).text
        job_type = driver.find_element(By.CSS_SELECTOR, job_work_type_selector).text
        job_post_date = driver.find_element(By.CSS_SELECTOR, job_post_date_selector).text
        job_salary_text = get_job_salary(driver)
        job_des = driver.find_element(By.CSS_SELECTOR, job_description_selector).text
        url = driver.current_url
        job_id = int(parse_qs(urlparse(url).query).get("jobId", [-1])[0])

        return JobAd(
            jobadid=job_id,
            job_title=job_title,
            company_name=company_name,
            job_loc=job_loc,
            job_type=job_type,
            job_post_date=job_post_date,
            job_salary_text=job_salary_text,
            job_description=job_des
        )
    except Exception as e:
        print(f"❌ Failed to extract job: {e}")
        return None
    
def main():
    # 設定瀏覽器驅動
    driver = setup_driver(headless=False)

    # 等待頁面載入
    driver.get("https://hk.jobsdb.com/android-jobs?page=1")
    driver.implicitly_wait(4)

    # 找出所有目標元素（同一 class 的 list）
    elements = driver.find_elements(By.CSS_SELECTOR, job_selector)
    print(f"Found {len(elements)} elements.")
    noOfSuccess = 0
    job_ads = []
    
    for idx, element in enumerate(elements):
        try:
            # 使用 ActionChains 滾動並點擊元素
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            # 等待滾動或點擊後變化
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, job_title_selector))
            )
            job_ad = extract_job(driver)
            if job_ad != None:
                job_ads.append(job_ad)
                noOfSuccess += 1
        except Exception as e:
            print(f"[{idx+1}] Click failed: {e}")
    session = get_session()        
    session.add_all(job_ads)  # 將所有 JobAd 實例添加到 session
    session.commit()  # 提交所有變更
    session.close()  # 關閉 session
    driver.quit()  # 關閉瀏覽器
    print(f'noOfSuccess={noOfSuccess}')
    # ----------------------------------


## main entry point
if __name__ == "__main__":
    main()
    