import json

import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo.driver import start_driver


@click.command()
@click.pass_context
@click.option(
    "--source",
    "-s",
    "source",
    type=click.Choice(["collection", "tops"]),
    default="collection",
    show_default=True,
    help="Source of fragrances, either a collection page or page of top fragrances.",
)
def import_fragrances(ctx, source):
    """Import an array of fragrance links from Parfumo pages."""
    config = ctx.obj.get("config")

    with start_driver() as driver:
        links = []
        # Collect fragrance urls from collection pages.
        if source == "collection":
            for page in tqdm(config["parfumo_collection_pages"]):
                driver.get(page["url"])
                for fragrance in tqdm(
                    driver.find_element(By.ID, "wr_wrapper").find_elements(
                        By.XPATH, "*"
                    )
                ):
                    fragrance.click()
                    try:
                        # Must keep this model in view at all times by scrolling down the page,
                        # following the progress of the loop.
                        link = driver.find_element(
                            By.CSS_SELECTOR,
                            "body > div.wr_sneak > div.header > div.img > a",
                        )
                        if link.get_attribute("href") in [l["link"] for l in links]:
                            print("Duplicate link, skipping...")
                            continue
                        links.append(
                            {"link": link.get_attribute("href"), "label": page["label"]}
                        )
                    except:
                        continue
        # Collect fragrance urls from top lists.
        elif source == "tops":
            for page in tqdm(config["parfumo_top_pages"]):
                driver.get(page["url"])
                for fragrance in tqdm(
                    driver.find_elements(By.XPATH, "//div[@class='image ']/a")
                ):
                    links.append(
                        {
                            "link": fragrance.get_attribute("href"),
                            "label": page["label"],
                        }
                    )

    with open(config["parfumo_import_results_path"], "w") as f:
        json.dump(links, f)
