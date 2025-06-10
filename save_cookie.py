import json
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"  # 如果你用 Firefox 官網版本

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def save_cookies(driver, filename="cookies.json"):
    # 建立 temp 資料夾（如果不存在）
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 設定完整路徑
    file_path = os.path.join(temp_dir, filename)
    
    cookies = driver.get_cookies()
    with open(file_path, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"[✔] Cookies saved to {file_path}")

def main():
    driver = setup_driver(headless=False)
    driver.get("https://hk.jobsdb.com/android-jobs?page=1")
    
    # 等候 cookies banner 同 dynamic JS 完成（你可用 WebDriverWait 寫得更穩）
    print("[...] Waiting for page to load and cookies to set...")
    time.sleep(30)

    save_cookies(driver)
    driver.close()

if __name__ == "__main__":
    main()
