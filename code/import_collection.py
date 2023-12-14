import json

import driver
from selenium.webdriver.common.by import By
from tqdm import tqdm

DRIVER = driver.start("https://www.parfumo.com")

collection_pages = [
    {
        "link": "https://www.parfumo.com/Users/Crazysillage/Collection/Abfuellungen",
        "label": "Decants",
    },
    {
        "link": "https://www.parfumo.com/Users/Crazysillage/Collection",
        "label": "I have",
    },
]
outfile = "data/parfumo/collection.json"

if __name__ == "__main__":
    links = []
    for page in tqdm(collection_pages):
        DRIVER.get(page["link"])
        for fragrance in tqdm(
            DRIVER.find_element(By.ID, "wr_wrapper").find_elements(By.XPATH, "*")
        ):
            fragrance.click()
            try:
                link = DRIVER.find_element(
                    By.CSS_SELECTOR, "body > div.wr_sneak > div.header > div.img > a"
                )
                links.append(
                    {"link": link.get_attribute("href"), "label": page["label"]}
                )
            except:
                continue

    with open(outfile, "w") as f:
        json.dump(links, f)
