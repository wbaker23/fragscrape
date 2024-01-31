from re import search

import click
import pandas as pd
import undetected_chromedriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


def get_year(name: str):
    try:
        year = search("(\d{4})$", name).group(0)
    except AttributeError:
        year = 0
    return year


def get_awarded_fragrances(url: str, driver):
    driver.get(url)
    count_fragrances = len(
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "nomination-box"))
        )
    )

    frag_list = []
    for i in tqdm(range(1, count_fragrances + 1)):
        try:
            name = driver.find_element(
                By.CSS_SELECTOR, f"div.small-6:nth-child({i}) > a:nth-child(2)"
            ).text
            link = driver.find_element(
                By.CSS_SELECTOR, f"div.small-6:nth-child({i}) > a:nth-child(2)"
            ).get_attribute("href")
            upvotes = driver.find_element(
                By.CSS_SELECTOR,
                f"div.small-6:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)",
            ).text
            downvotes = driver.find_element(
                By.CSS_SELECTOR,
                f"div.small-6:nth-child({i}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)",
            ).text
            year = get_year(name)

            frag_list.append(
                {
                    "name": name,
                    "link": link,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "year": year,
                    "order": i,
                }
            )
        except (NoSuchElementException, AttributeError):
            print(name, link, upvotes, downvotes, year)
            break
    return frag_list


@click.command()
@click.pass_context
def load(ctx):
    config = ctx.obj.get("config")

    with undetected_chromedriver.Chrome() as driver:
        driver.implicitly_wait(10)
        for page in config["fragrantica_awards_pages_to_import"]:
            print(f"Processing {page['url']}")
            filename = f"{config['import_data_path']}/{page['name']}.csv"
            pd.DataFrame(get_awarded_fragrances(page["url"], driver)).to_csv(
                filename, index=False
            )
            print(f"Wrote {filename}")
