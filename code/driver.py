import undetected_chromedriver


def start():
    DRIVER = undetected_chromedriver.Chrome()
    DRIVER.implicitly_wait(10)
    input("Press enter when driver is ready:")
    return DRIVER
