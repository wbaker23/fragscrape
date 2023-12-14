import json
import re

import driver
from selenium.webdriver.common.by import By
from tqdm import tqdm

DRIVER = driver.start("https://www.parfumo.com")

infile = "data/parfumo/collection.json"
outfile = "data/parfumo/collection_enriched.json"

if __name__ == "__main__":
    with open(infile, "r") as f:
        collection = json.load(f)

    decants_enriched = []
    for fragrance in tqdm(collection):
        DRIVER.get(fragrance)
        name = DRIVER.find_element(
            By.CSS_SELECTOR, "#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1"
        ).text
        brand = DRIVER.find_element(
            By.CSS_SELECTOR,
            "#pd_inf > div.cb.pt-1 > main > div.p_details_holder > h1 > span > span > a:nth-child(1) > span",
        ).text

        try:
            DRIVER.find_element(By.ID, "classi_li").click()
            type_script = DRIVER.find_element(
                By.CSS_SELECTOR, "#classification_community > script:nth-child(2)"
            ).get_attribute("innerHTML")
            scent_type = json.loads(
                re.search("chart4\.data = ([^;]+)", type_script).group(1)
            )
        except:
            scent_type = None

        try:
            occasion_script = DRIVER.find_element(
                By.CSS_SELECTOR, "#classification_community > script:nth-child(14)"
            ).get_attribute("innerHTML")
            scent_occasion = json.loads(
                re.search("chart2\.data = ([^;]+)", occasion_script).group(1)
            )
        except:
            scent_occasion = None

        try:
            audience_script = DRIVER.find_element(
                By.CSS_SELECTOR, "#classification_community > script:nth-child(6)"
            ).get_attribute("innerHTML")
            scent_audience = json.loads(
                re.search("chart1\.data = ([^;]+)", audience_script).group(1)
            )
        except:
            scent_audience = None

        try:
            season_script = DRIVER.find_element(
                By.CSS_SELECTOR, "#classification_community > script:nth-child(10)"
            ).get_attribute("innerHTML")
            scent_season = json.loads(
                re.search("chart3\.data = ([^;]+)", season_script).group(1)
            )
        except:
            scent_season = None

        decants_enriched.append(
            {
                "name": name,
                "brand": brand,
                "link": fragrance,
                "type": scent_type,
                "occasion": scent_occasion,
                "audience": scent_audience,
                "season": scent_season,
            }
        )

    with open(outfile, "w") as f:
        json.dump(decants_enriched, f)
