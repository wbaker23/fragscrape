import statistics
from re import findall, search

import pandas as pd
import undetected_chromedriver
from scipy.stats import beta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from fragscrape.fragrantica.config import *

DRIVER = undetected_chromedriver.Chrome()
DRIVER.implicitly_wait(10)


def get_year(name: str):
    try:
        year = search("(\d{4})$", name).group(0)
    except AttributeError:
        year = 0
    return year


def get_awarded_fragrances(url: str):
    DRIVER.get(url)
    count_fragrances = len(
        WebDriverWait(DRIVER, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "nomination-box"))
        )
    )

    frag_list = []
    for i in tqdm(range(1, count_fragrances + 1)):
        try:
            name = DRIVER.find_element(
                By.CSS_SELECTOR, f"div.small-6:nth-child({i}) > a:nth-child(2)"
            ).text
            link = DRIVER.find_element(
                By.CSS_SELECTOR, f"div.small-6:nth-child({i}) > a:nth-child(2)"
            ).get_attribute("href")
            upvotes = DRIVER.find_element(
                By.CSS_SELECTOR,
                f"div.small-6:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)",
            ).text
            downvotes = DRIVER.find_element(
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


def positive_votes(x, **kwargs):
    return x[1][1]


def vote_difference(x, **kwargs):
    diff = x[1][1] - x[1][2]
    return diff


def bayesian_rating(x, **kwargs):
    a = x[1][1] + kwargs["avg_pos_votes"]
    b = x[1][2] + kwargs["avg_neg_votes"]
    rank = beta.ppf(0.05, a, b)
    return rank


def print_console_and_file(text, file):
    if file != None:
        print(text, file=file)
    print(text)


def print_list(
    file_name,
    frag_dict,
    min_year=0,
    max_year=3000,
    cutoff=1,
    ranking_func=bayesian_rating,
    max_print=50,
    include_female=True,
):
    if file_name != None:
        out_file = open(file_name, "w")
    else:
        out_file = None

    avg_pos_votes = statistics.mean([item[1][1] for item in frag_dict.items()])
    avg_neg_votes = statistics.mean([item[1][2] for item in frag_dict.items()])
    filtered_dict = dict()

    i = 0
    for key, value in sorted(
        frag_dict.items(),
        key=lambda x: ranking_func(
            x, avg_pos_votes=avg_pos_votes, avg_neg_votes=avg_neg_votes
        ),
        reverse=True,
    ):
        if (
            value[0] in [*range(min_year, max_year + 1)]
            and value[1] >= cutoff
            and i < max_print
        ):
            if include_female:
                filtered_dict[key] = value
                i = i + 1
            else:
                if "female" not in findall("\((\w*?)\)", key):
                    filtered_dict[key] = value
                    i = i + 1

    name_spaces = max([len(item[0]) for item in filtered_dict.items()]) + 2
    total_spaces = name_spaces + 32
    print_console_and_file("-" * total_spaces, file=out_file)
    print_console_and_file(
        "{1:<{0}s}{2:>10s}{3:>10s}{4:>12s}".format(
            name_spaces, "Name", "Year", "Upvotes", "Ratio"
        ),
        file=out_file,
    )
    print_console_and_file("-" * total_spaces, file=out_file)

    for key, value in sorted(
        filtered_dict.items(),
        key=lambda x: ranking_func(
            x, avg_pos_votes=avg_pos_votes, avg_neg_votes=avg_neg_votes
        ),
        reverse=True,
    ):
        ratio = value[1] / (value[1] + value[2]) if (value[1] + value[2]) > 0 else 1
        print_console_and_file(
            "{1:<{0}s}{2:>10d}{3:>10d}{4:>12f}".format(
                name_spaces, key, int(value[0]), int(value[1]), ratio
            ),
            file=out_file,
        )


def graph_years(frag_dict, ranking_func=bayesian_rating):
    avg_pos_votes = statistics.mean([item[1][1] for item in frag_dict.items()])
    avg_neg_votes = statistics.mean([item[1][2] for item in frag_dict.items()])

    x = [item[1][0] for item in frag_dict.items()]
    y = [
        ranking_func(item, avg_pos_votes=avg_pos_votes, avg_neg_votes=avg_neg_votes)
        for item in frag_dict.items()
    ]

    return x, y


if __name__ == "__main__":
    for name, link in PAGES_TO_IMPORT.items():
        print(f"Processing {link}")
        filename = f"{DATA_PATH}/raw/{name}.csv"
        pd.DataFrame(get_awarded_fragrances(link)).to_csv(filename, index=False)
        print(f"Wrote {filename}")
    DRIVER.close()
