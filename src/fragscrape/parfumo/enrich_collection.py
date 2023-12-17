import json
import re

import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo.driver import start_driver


@click.command()
@click.pass_context
def enrich_collection(ctx):
    config = ctx.obj.get("config")

    with open(config["parfumo_import_results_path"], "r") as f:
        collection = json.load(f)

    with start_driver() as driver:
        decants_enriched = []
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

            try:
                driver.find_element(By.ID, "classi_li").click()
                type_script = driver.find_element(
                    By.CSS_SELECTOR, "#classification_community > script:nth-child(2)"
                ).get_attribute("innerHTML")
                scent_type = json.loads(
                    re.search("chart4\\.data = ([^;]+)", type_script).group(1)
                )
            except:
                scent_type = None

            try:
                occasion_script = driver.find_element(
                    By.CSS_SELECTOR, "#classification_community > script:nth-child(14)"
                ).get_attribute("innerHTML")
                scent_occasion = json.loads(
                    re.search("chart2\\.data = ([^;]+)", occasion_script).group(1)
                )
            except:
                scent_occasion = None

            try:
                audience_script = driver.find_element(
                    By.CSS_SELECTOR, "#classification_community > script:nth-child(6)"
                ).get_attribute("innerHTML")
                scent_audience = json.loads(
                    re.search("chart1\\.data = ([^;]+)", audience_script).group(1)
                )
            except:
                scent_audience = None

            try:
                season_script = driver.find_element(
                    By.CSS_SELECTOR, "#classification_community > script:nth-child(10)"
                ).get_attribute("innerHTML")
                scent_season = json.loads(
                    re.search("chart3\\.data = ([^;]+)", season_script).group(1)
                )
            except:
                scent_season = None

            decants_enriched.append(
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
        json.dump(decants_enriched, f)
