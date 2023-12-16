import json

from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.helpers import driver

DRIVER = driver.start("https://www.parfumo.com")

# TODO: Parameterize this
collection_pages = [
    {
        "link": "https://www.parfumo.com/Users/Crazysillage/Collection/Abfuellungen",
        "label": "Decants",
    },
    {
        "link": "https://www.parfumo.com/Users/Crazysillage/Collection",
        "label": "I have",
    },
    {
        "link": "https://www.parfumo.com/Users/Crazysillage/Collection/Wish_List",
        "label": "Wish List",
    },
]
# TODO: and this
outfile = "data/parfumo/fragrance_links.json"

if __name__ == "__main__":
    links = []
    for page in tqdm(collection_pages):
        DRIVER.get(page["link"])
        for fragrance in tqdm(
            DRIVER.find_element(By.ID, "wr_wrapper").find_elements(By.XPATH, "*")
        ):
            fragrance.click()
            try:
                # Must keep this model in view at all times by scrolling down the page,
                # following the progress of the loop.
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
