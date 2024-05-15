import json
import re

import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo.driver import start_driver


def _get_chart_data(driver, i, j):
    try:
        driver.find_element(By.XPATH, "//nav[@class='flex ptabs ']/div[6]").click()
        script = driver.find_element(
            By.CSS_SELECTOR, f"#classification_community > script:nth-child({i})"
        ).get_attribute("innerHTML")
        type = json.loads(re.search(f"chart{j}\\.data = ([^;]+)", script).group(1))
    except:
        type = None
    finally:
        return type


@click.command()
@click.pass_context
def enrich(ctx):
    """Navigate to previously scraped fragrance urls to get categorization data."""
    config = ctx.obj.get("config")

    with open(config["parfumo_import_results_path"], "r") as f:
        collection = json.load(f)

    with start_driver() as driver:
        fragrances_enriched = []
        # Let this loop run with the Chrome driver on screen, and wait until it finishes.
        for fragrance in tqdm(collection):
            driver.get(fragrance["link"])
            name = driver.find_element(
                By.CSS_SELECTOR,
                "#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1",
            ).text
            brand = driver.find_element(
                By.CSS_SELECTOR,
                "#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(1) > span",
            ).text
            image_src = driver.find_element(
                By.XPATH, "//img[@itemprop='image']"
            ).get_attribute("src")

            scent_type = _get_chart_data(driver, 2, 4)
            scent_occasion = _get_chart_data(driver, 14, 2)
            scent_audience = _get_chart_data(driver, 6, 1)
            scent_season = _get_chart_data(driver, 10, 3)

            fragrances_enriched.append(
                {
                    "name": name,
                    "brand": brand,
                    "image_src": image_src,
                    "link": fragrance["link"],
                    "type": scent_type,
                    "occasion": scent_occasion,
                    "audience": scent_audience,
                    "season": scent_season,
                    "collection_group": fragrance["label"],
                }
            )

        with open(config["parfumo_enrich_results_path"], "w") as f:
            json.dump(fragrances_enriched, f)
