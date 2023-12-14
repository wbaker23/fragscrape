import undetected_chromedriver


def start(url):
    DRIVER = undetected_chromedriver.Chrome()
    DRIVER.implicitly_wait(10)
    DRIVER.get(url)
    input("Press enter when driver is ready:")
    return DRIVER
