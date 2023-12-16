import time

import undetected_chromedriver
from selenium.webdriver.common.by import By


def _close_parfumo_cookies_popup(driver):
    iframe = driver.find_element(By.XPATH, "//iframe[@title='SP Consent Message']")
    driver.switch_to.frame(iframe)
    driver.find_element(By.XPATH, "//button[@title='Settings or reject']").click()
    time.sleep(3)

    driver.switch_to.default_content()

    iframe = driver.find_element(By.XPATH, "(//iframe[@title='SP Consent Message'])[2]")
    driver.switch_to.frame(iframe)
    driver.find_element(By.XPATH, "//button[@title='Save & Exit']").click()
    time.sleep(3)

    return driver


def start_driver():
    DRIVER = undetected_chromedriver.Chrome()
    DRIVER.implicitly_wait(10)
    DRIVER.get("https://www.parfumo.com")
    DRIVER = _close_parfumo_cookies_popup(DRIVER)
    return DRIVER
