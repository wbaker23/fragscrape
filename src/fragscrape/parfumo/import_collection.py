import json

import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo.driver import start_driver


@click.command()
@click.pass_context
def import_collection(ctx):
    config = ctx.obj.get("config")

    with start_driver() as driver:
        links = []
        for page in tqdm(config["parfumo_collection_pages"]):
            driver.get(page["url"])
            for fragrance in tqdm(
                driver.find_element(By.ID, "wr_wrapper").find_elements(By.XPATH, "*")
            ):
                fragrance.click()
                try:
                    # Must keep this model in view at all times by scrolling down the page,
                    # following the progress of the loop.
                    link = driver.find_element(
                        By.CSS_SELECTOR,
                        "body > div.wr_sneak > div.header > div.img > a",
                    )
                    links.append(
                        {"link": link.get_attribute("href"), "label": page["label"]}
                    )
                except:
                    continue

    with open(config["parfumo_import_results_path"], "w") as f:
        json.dump(links, f)
