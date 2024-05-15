import json
import re
from collections import Counter
from itertools import chain

import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo.driver import start_driver


def _add_note_groups(driver, fragrances_enriched: list, write_path: str):
    notes_list = set(chain.from_iterable(f["notes"] for f in fragrances_enriched))
    replacement_dict = {
        "Mandarin_orange": "Mandarin",
        "Green_mandarin_orange": "Green_mandarin",
        "Ylang-ylang": "Ylang_ylang",
        "Italian_mandarin_orange": "Italian_mandarin",
        "Italian_green_mandarin_orange": "Italian_green_mandarin",
        "Calabrian_mandarin_orange": "Calabrian_mandarin",
        "Sicilian_mandarin_orange": "Sicilian_mandarin",
        "Green_stems": "green-stem",
        "Roman_chamomile": "roman-camomile",
        "Frankincense_resin": "frankincense",
        "Oak_wood_absolute": "Oak_absolute",
        "Red_mandarin_orange": "Red_mandarin",
        "Papua_New_Guinean_vanilla": "papua-new-guinea-vanilla",
    }
    note_groups_dict = {}

    for n in tqdm(notes_list):
        url_name = n
        url_name = url_name.replace("®", "")
        url_name = url_name.replace("™", "")
        url_name = url_name.replace("é", "e")
        url_name = url_name.replace("ç", "c")
        url_name = url_name.replace(" ", "_")
        if url_name in replacement_dict:
            driver.get(
                f"https://www.parfumo.com/Fragrance_Note/{replacement_dict[url_name]}"
            )
        else:
            driver.get(f"https://www.parfumo.com/Fragrance_Note/{url_name}")
        try:
            driver.find_element(By.XPATH, "//div[@class='main']")
            groups = driver.find_elements(
                By.XPATH, "//div[@class='mt-1 mb-1']/span[@class='label_a upper']/a"
            )
            note_groups_dict[n] = [group.get_attribute("href") for group in groups]
        except:
            try:
                driver.get(
                    f"https://www.parfumo.com/Fragrance_Note/{url_name.lower().replace('_', '-')}"
                )
                driver.find_element(By.XPATH, "//div[@class='main']")
                groups = driver.find_elements(
                    By.XPATH,
                    "//div[@class='mt-1 mb-1']/span[@class='label_a upper']/a",
                )
                note_groups_dict[n] = [group.get_attribute("href") for group in groups]
            except:
                print(url_name)

    with open(write_path, "w") as f:
        json.dump(note_groups_dict, f)

    for f in fragrances_enriched:
        notes_list = list(zip(f["notes"], f["notes_strength"]))
        note_groups = {}
        for n in notes_list:
            for g in note_groups_dict[n[0]]:
                if g in note_groups:
                    note_groups[g] += n[1]
                else:
                    note_groups[g] = n[1]
        f["note_groups"] = [
            {"group_name": l[0], "group_count": l[1]} for l in note_groups.items()
        ]

    return fragrances_enriched


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

            notes_list = []
            notes_strength = []
            for e in driver.find_elements(
                By.XPATH,
                "//div[@class='notes_list mb-2']//span[@class='nowrap pointer']//img",
            ):
                notes_list.append(e.get_attribute("alt"))
                notes_strength.append(int(e.get_attribute("class")[-1]))

            try:
                driver.find_element(
                    By.XPATH, "//nav[@class='flex ptabs ']/div[6]"
                ).click()
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
                    "notes": notes_list,
                    "notes_strength": notes_strength,
                }
            )

        # Checkpoint
        with open(config["parfumo_enrich_results_path"], "w") as f:
            json.dump(fragrances_enriched, f)

        fragrances_enriched = _add_note_groups(
            driver, fragrances_enriched, config["parfumo_enrich_notes_path"]
        )

        # Final write
        with open(config["parfumo_enrich_results_path"], "w") as f:
            json.dump(fragrances_enriched, f)
