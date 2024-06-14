import time

import undetected_chromedriver
from selenium.webdriver.common.by import By


def _close_parfumo_cookies_popup(driver):
    """Automatically close Parfumo's cookie dialogs."""
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


def start_driver(username: str = None, password: str = None):
    """Initialize driver and navigate to Parfumo."""
    driver = undetected_chromedriver.Chrome()
    driver.implicitly_wait(10)
    driver.get("https://www.parfumo.com")
    driver = _close_parfumo_cookies_popup(driver)

    if username is not None and password is not None:
        driver.find_element(By.ID, "login-btn").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button").click()

    return driver
