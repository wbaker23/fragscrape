import json

import driver
from selenium.webdriver.common.by import By
from tqdm import tqdm

DRIVER = driver.start("https://www.parfumo.com")

collection_pages = [
    "https://www.parfumo.com/Users/Crazysillage/Collection/Abfuellungen",
    "https://www.parfumo.com/Users/Crazysillage/Collection",
]
outfile = "data/parfumo/collection.json"

if __name__ == "__main__":
    links = []
    for page in tqdm(collection_pages):
        DRIVER.get(page)
        for fragrance in tqdm(
            DRIVER.find_element(By.ID, "wr_wrapper").find_elements(By.XPATH, "*")
        ):
            fragrance.click()
            try:
                link = DRIVER.find_element(
                    By.CSS_SELECTOR, "body > div.wr_sneak > div.header > div.img > a"
                )
                links.append(link.get_attribute("href"))
            except:
                continue

    with open(outfile, "w") as f:
        json.dump(links, f)
