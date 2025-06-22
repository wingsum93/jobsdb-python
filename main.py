from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selector import PostSelector, ListSelector
from urllib.parse import urlparse, parse_qs
from fetch.db.model import JobAd
from db import insert_all_job_ads
import json
import os


def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # Pretend Firefox User-Agent
    firefox_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
    options.add_argument(f'--user-agent={firefox_user_agent}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def load_cookies(driver, filename="cookies.json"):
    # 組合 temp 資料夾的完整路徑
    temp_dir = os.path.join(os.getcwd(), "temp")
    file_path = os.path.join(temp_dir, filename)
    
    # 檢查檔案是否存在
    if not os.path.exists(file_path):
        print(f"[✘] 找不到 cookie 檔案：{file_path}")
        return
    with open(file_path, "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()  # 刷新頁面以應用 cookies
# ----------------------------------
### container for outer conteainer 
### div block _1oozmqe0 l218ib5b l218ibhf l218ib6v


### tried job selectors
### div._1oozmqe0.l218ib4v.l218ib51 a[data-automation="job-list-item-link-overlay"]
### a[data-automation="jobTitle"]


def have_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, ListSelector.NEXT_PAGE_BTN)
        # Check if the button is visible and not hidden by 'aria-hidden'
        is_visible = next_button.is_displayed()
        aria_hidden = next_button.get_attribute('aria-hidden')  # Correct method
        # Also consider checking if the button is enabled
        return is_visible and aria_hidden != 'true' and next_button.is_enabled()
    except Exception as e:
        print(f"❌ Error checking for next page: {e}")
        return False
    
def go_to_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, ListSelector.NEXT_PAGE_BTN)
        next_button.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ListSelector.JOB))
        )
    except Exception as e:
        print(f"❌ Error going to next page: {e}")

def get_job_salary(driver):
    try:
        job_detail_salary = driver.find_element(By.CSS_SELECTOR,PostSelector.DETAIL_SALARY)
        return job_detail_salary.text
    except Exception as e:
        job_expected_salary = driver.find_element(By.CSS_SELECTOR,PostSelector.EXPECTED_SALARY)
        return job_expected_salary.text
def extract_job(driver):
    try:
        job_title = driver.find_element(By.CSS_SELECTOR, PostSelector.TITLE).text
        company_name = driver.find_element(By.CSS_SELECTOR, PostSelector.COMPANY_NAME).text
        job_loc = driver.find_element(By.CSS_SELECTOR, PostSelector.LOCATION).text
        job_type = driver.find_element(By.CSS_SELECTOR, PostSelector.WORK_TYPE).text
        job_post_date = ''#driver.find_element(By.CSS_SELECTOR, PostSelector.POST_DATE).text
        job_salary_text = get_job_salary(driver)
        job_des = driver.find_element(By.CSS_SELECTOR, PostSelector.DESCRIPTION).text
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
def get_total_job_count(driver):
    try:
        total_count_element = driver.find_element(By.CSS_SELECTOR, ListSelector.JOB_NUMBER_COUNT_A)
        return int(total_count_element.text.replace(',', ''))
    except Exception as e:
        print(f"❌ Error getting total job count: {e}")
        return 0
    
def loop_through_one_page(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, ListSelector.JOB)
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
                EC.presence_of_element_located((By.CSS_SELECTOR, PostSelector.TITLE))
            )
            job_ad = extract_job(driver)
            if job_ad != None:
                job_ads.append(job_ad)
                noOfSuccess += 1
        except Exception as e:
            print(f"[{idx+1}] Click failed: {e}")
    insert_all_job_ads(job_ads)
    return noOfSuccess
    
def main(load_cookies=False):
    # 設定瀏覽器驅動
    driver = setup_driver(headless=False)

    # 等待頁面載入
    driver.get("https://hk.jobsdb.com/android-jobs?page=1")
    if(load_cookies):
        load_cookies(driver)  # 載入 cookies
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, total_job_number_count_selector))
    # )
    driver.implicitly_wait(5)  # 等待元素載入

    # get total job count
    #total_job_count = get_total_job_count(driver)
    current_page_number = 1
    total_number_of_jobs_extracted = 0
    
    ## extract first page
    noOfSuccess = 0
    noOfSuccess = loop_through_one_page(driver)

    while have_next_page(driver):
        go_to_next_page(driver)
        current_page_number += 1
        print(f"Processing page {current_page_number}...")
        noOfSuccess = loop_through_one_page(driver)
        print(f"Page {current_page_number} processed with {noOfSuccess} successful job ads.")
        total_number_of_jobs_extracted += noOfSuccess





    #print(f"Total job count: {total_job_count}")
    print(f"Total number of jobs extracted: {total_number_of_jobs_extracted}")
    driver.close()  # 關閉瀏覽器
    
    # ----------------------------------


## main entry point
if __name__ == "__main__":
    main()
    