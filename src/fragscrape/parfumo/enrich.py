import json
import re
from datetime import datetime

import click
from selenium.webdriver.common.by import By
from tqdm import tqdm

from fragscrape.parfumo import database
from fragscrape.parfumo.driver import start_driver


def _get_chart_data(driver, i, j, open_charts=False):
    chart_button = driver.find_element(
        By.XPATH,
        f"//nav[@class='flex ptabs ']/div[@class='action_order_pd action_order_classification{'' if open_charts else ' active'}']",
    )
    if chart_button.get_attribute("innerHTML") == "<span>Chart</span>":
        chart_button.click()
        script = driver.find_element(
            By.CSS_SELECTOR, f"#classification_community > script:nth-child({i})"
        ).get_attribute("innerHTML")
        data = json.loads(re.search(f"chart{j}\\.data = ([^;]+)", script).group(1))
    else:
        data = None
    return data


@database.db_cursor
def _get_collection(cursor):
    return [
        dict(o)
        for o in cursor.execute(
            "SELECT * FROM collection WHERE collection_group != 'I Had'"
        ).fetchall()
    ]


@database.db_cursor
def _get_votes(cursor):
    return {
        row["link"]: row["min(last_updated)"]
        for row in cursor.execute(
            "SELECT link, min(last_updated) FROM votes GROUP BY link"
        ).fetchall()
    }


@database.db_cursor
def _get_tops(cursor):
    return [dict(o) for o in cursor.execute("SELECT * FROM tops").fetchall()]


@database.db_cursor
def _update_collection_row(cursor, data):
    cursor.execute(
        """
        UPDATE collection SET
        name = :name,
        brand = :brand,
        image_src = :image_src
        WHERE link = :link
        """,
        data,
    )


@database.db_cursor
def _update_tops_row(cursor, data):
    cursor.execute(
        """
        UPDATE tops SET
        name = :name,
        brand = :brand,
        image_src = :image_src
        WHERE link = :link
        """,
        data,
    )


@database.db_cursor
def _update_votes_rows(cursor, data):
    cursor.executemany(
        """
        INSERT INTO votes (link, category, votes, last_updated) 
        VALUES (:link, :category, :votes, DATE('now'))
        ON CONFLICT(link, category) DO UPDATE
        SET votes = excluded.votes, last_updated = DATE('now')
        """,
        data,
    )


@click.command()
@click.option(
    "--source",
    "-s",
    "source",
    type=click.Choice(["collection", "tops"]),
    default="collection",
    show_default=True,
    help="Source of fragrances, either a collection page or page of top fragrances.",
)
def enrich(source):
    """Navigate to previously scraped fragrance urls to get categorization data."""
    if source == "collection":
        # pylint: disable-next=no-value-for-parameter
        data = _get_collection()
    elif source == "tops":
        # pylint: disable-next=no-value-for-parameter
        data = _get_tops()

    vote_data = _get_votes()

    with start_driver() as driver:
        # Let this loop run with the Chrome driver on screen, and wait until it finishes.
        for fragrance in tqdm(data):
            if fragrance["link"] in vote_data.keys():
                if vote_data[fragrance["link"]] == datetime.utcnow().date().isoformat():
                    continue

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
                scent_type = _get_chart_data(driver, 2, 4, open_charts=True)
                scent_occasion = _get_chart_data(driver, 14, 2)
                scent_audience = _get_chart_data(driver, 6, 1)
                scent_season = _get_chart_data(driver, 10, 3)

                all_votes = [
                    *scent_type,
                    *scent_occasion,
                    *scent_audience,
                    *scent_season,
                ]
                for item in all_votes:
                    item["link"] = fragrance["link"]
                    item["category"] = item["ct_name"]

                if source == "collection":
                    # pylint: disable-next=no-value-for-parameter
                    _update_collection_row(
                        {
                            "name": name,
                            "brand": brand,
                            "image_src": image_src,
                            "link": fragrance["link"],
                        }
                    )
                elif source == "tops":
                    # pylint: disable-next=no-value-for-parameter
                    _update_tops_row(
                        {
                            "name": name,
                            "brand": brand,
                            "image_src": image_src,
                            "link": fragrance["link"],
                        }
                    )

                # pylint: disable-next=no-value-for-parameter
                _update_votes_rows(all_votes)
            except:
                print(fragrance["link"])
                continue
