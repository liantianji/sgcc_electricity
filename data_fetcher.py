import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import ddddocr
import time
import logging
import traceback
import subprocess
import re
from const import *


class DataFetcher:

    def __init__(self, username: str, password: str):

        self._username = username
        self._password = password
        self._ocr = ddddocr.DdddOcr(show_ad = False)
        self._chromium_version = self._get_chromium_version()

    
    def fetch(self):
        for retry_times in range(1, RETRY_TIMES_LIMIT + 1):
            try:
                return self._fetch()
            except Exception as e:
                if(retry_times == RETRY_TIMES_LIMIT):
                    raise e
                traceback.print_exc()
                logging.error(f"Webdriver quit abnormly, reason: {e}. {RETRY_TIMES_LIMIT - retry_times} retry times left.")
                wait_time = retry_times * RETRY_WAIT_TIME_OFFSET_UNIT
                time.sleep(wait_time)
                
            
    
    def _fetch(self):
        driver = self._get_webdriver()
        logging.info("Webdriver initialized.")
        try:
            self._login(driver)
            logging.info(f"Login successfully on {LOGIN_URL}" )
            balance = self._get_eletric_balance(driver)
            logging.info(f"Get electricity charge balance successfully, balance is {balance} CNY.")
            usage = self._get_yesterday_usage(driver)
            logging.info(f"Get yesterday power consumption successfully, usage is {usage} kwh.")
            driver.quit()
            logging.debug("Webdriver quit after fetching data successfully.")
            return balance, usage
        finally:
                driver.quit()  

    def _get_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--window-size=4000,1600')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage') 
        driver = uc.Chrome(options = chrome_options, version_main = self._chromium_version)
        driver.implicitly_wait(DRIVER_IMPLICITY_WAIT_TIME)
        return driver

    def _login(self, driver):
        driver.get(LOGIN_URL)
        driver.find_element(By.CLASS_NAME,"user").click()
        input_elements = driver.find_elements(By.CLASS_NAME,"el-input__inner")
        input_elements[0].send_keys(self._username)
        input_elements[1].send_keys(self._password)
        
        
        captcha_element = driver.find_element(By.CLASS_NAME,"code-mask")
        
        for retry_times in range(1, RETRY_TIMES_LIMIT + 1):

            img_src = captcha_element.find_element(By.TAG_NAME,"img").get_attribute("src")
            img_base64 = img_src.replace("data:image/jpg;base64,","")
            orc_result = str(self._ocr.classification(ddddocr.base64_to_image(img_base64)))

            if(not self._is_captcha_legal(orc_result)):
                logging.debug(f"The captcha is illegal, which is caused by ddddocr, {RETRY_TIMES_LIMIT - retry_times} retry times left.")
                captcha_element.click()
                time.sleep(2)
                continue

            input_elements[2].send_keys(orc_result)

            driver.find_element(By.CLASS_NAME, "el-button.el-button--primary").click()
            try:
                return WebDriverWait(driver,LOGIN_EXPECTED_TIME).until(EC.url_changes(LOGIN_URL))
            except:
                logging.debug(f"Login failed, maybe caused by invalid captcha, {RETRY_TIMES_LIMIT - retry_times} retry times left.")

        raise Exception("Login failed, please check your phone number and password!!!")

    def _get_eletric_balance(self, driver):
        driver.find_element(By.XPATH,"//li[@class='inline_block_fix zhanghu-full']//b[@class='cff8']")
        time.sleep(5)
        for retry_times in range(0, RETRY_TIMES_LIMIT):
            electric_balance = driver.find_element(By.XPATH,"//li[@class='inline_block_fix zhanghu-full']//b[@class='cff8']").text
            if(not electric_balance.startswith("-")):
                break
            time.sleep(1)
        return float(electric_balance.replace("元",""))
    
    def _get_yesterday_usage(self, driver):
        driver.get(ELECTRIC_USAGE_URL)
        driver.find_element(By.XPATH,"//div[@class='el-tabs__nav is-top']/div[@id='tab-second']").click()
        usage = driver.find_element(By.XPATH,"//div[@class='el-table__body-wrapper is-scrolling-none']//td[@class='el-table_2_column_6  ']/div").text
        return(float(usage))

    @staticmethod
    def _is_captcha_legal(captcha):
        if(len(captcha) != 4): 
            return False
        for s in captcha:
            if(not s.isalpha() and not s.isdigit()):
                return False
        return True
    
    @staticmethod
    def _get_chromium_version():
        result = str(subprocess.check_output(["chromium", "--product-version"]))
        return re.findall(r"(\d*)\.",result)[0]
