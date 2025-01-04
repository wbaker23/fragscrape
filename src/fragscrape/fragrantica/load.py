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
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[starts-with(@id, 'nomination_')]")
            )
        )
    )
    nominations = driver.find_elements(
        By.XPATH, "//div[starts-with(@id, 'nomination_')]"
    )
    assert len(nominations) == count_fragrances

    frag_list = []
    for nomination in tqdm(nominations):
        try:
            info = nomination.find_element(By.CSS_SELECTOR, "p > a")
            name = info.text
            link = info.get_attribute("href")

            upvotes = nomination.find_element(
                By.CSS_SELECTOR,
                "div.flex.justify-between.items-center.pt-3.pb-2.px-1.bg-clip-padding.bg-gradient-to-b.from-neutral-50.to-white.max-lg\:rounded-t-\[1rem\].lg\:rounded-tl-\[0\.5rem\].lg\:rounded-tr-\[0\.5rem\] > div:nth-child(1) > div.flex.flex-col.justify-end.items-center.h-full.w-full.cursor-pointer > div > span",
            ).text
            downvotes = driver.find_element(
                By.CSS_SELECTOR,
                "div.flex.justify-between.items-center.pt-3.pb-2.px-1.bg-clip-padding.bg-gradient-to-b.from-neutral-50.to-white.max-lg\:rounded-t-\[1rem\].lg\:rounded-tl-\[0\.5rem\].lg\:rounded-tr-\[0\.5rem\] > div:nth-child(2) > div.flex.flex-col.justify-end.items-center.h-full.w-full.cursor-pointer > div > span",
            ).text
            year = get_year(name)

            frag_list.append(
                {
                    "name": name,
                    "link": link,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "year": year,
                    "order": nominations.index(nomination),
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
