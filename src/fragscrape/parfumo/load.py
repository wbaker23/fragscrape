import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo import database
from fragscrape.parfumo.driver import start_driver

# pylint: disable-next=no-value-for-parameter
database.initialize()


@database.db_cursor
def _load_collection(cursor, driver, pages):
    links = []

    for page in tqdm(pages):
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
                if link.get_attribute("href") in [l["link"] for l in links]:
                    continue
                links.append(
                    {"link": link.get_attribute("href"), "label": page["label"]}
                )
            except:
                continue

    cursor.executemany(
        """
        INSERT INTO collection (link, collection_group) 
        VALUES (:link, :label) 
        ON CONFLICT DO UPDATE 
        SET collection_group = excluded.collection_group
        """,
        links,
    )

    return links


@database.db_cursor
def _load_tops(cursor, driver, pages):
    links = []

    for page in tqdm(pages):
        driver.get(page["url"])
        links.extend(
            {
                "link": fragrance.get_attribute("href"),
                "label": page["label"],
            }
            for fragrance in tqdm(
                driver.find_elements(By.XPATH, "//div[@class='image ']/a")
            )
        )

    cursor.executemany(
        """
        INSERT INTO tops (link, collection_group) 
        VALUES (:link, :label) 
        ON CONFLICT DO UPDATE 
        SET collection_group = excluded.collection_group
        """,
        links,
    )

    return links


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
def load(ctx, source):
    """Import an array of fragrance links from Parfumo pages."""
    config = ctx.obj.get("config")

    with start_driver() as driver:
        if source == "collection":
            # pylint: disable-next=no-value-for-parameter
            links = _load_collection(driver, config["parfumo_pages"])
        elif source == "tops":
            # pylint: disable-next=no-value-for-parameter
            links = _load_tops(driver, config["parfumo_pages"])
