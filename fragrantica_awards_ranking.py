from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from pandas import read_csv, DataFrame, Series

import sys
from re import search, sub, findall
from ast import literal_eval
from numpy import int64, isnan, NaN
import numpy as np
from scipy.stats import beta
import statistics


def get_awards_votes(driver, url):
    index = url.rindex("/") + 1
    file_name = url[index:] + ".txt"
    driver.get(url)
    frag_dict = dict()
    i = 1
    while True:
        try:
            name = driver.find_element(
                By.CSS_SELECTOR, f"div.cell:nth-child({i}) > a:nth-child(2)"
            ).text
            upvotes = driver.find_element(
                By.CSS_SELECTOR,
                f"div.small-6:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)",
            ).text
            downvotes = driver.find_element(
                By.CSS_SELECTOR,
                f"div.small-6:nth-child({i}) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)",
            ).text
            year = name[-4:]
            try:
                frag_dict[name[:-7]] = (int(year), int(upvotes), int(downvotes))
            except:
                frag_dict[name[:-7]] = (np.nan, int(upvotes), int(downvotes))
            i = i + 1
        except:
            break
    return file_name, frag_dict


def vote_difference(x, **kwargs):
    diff = x[1][1] - x[1][2]
    return diff


def bayesian_rating(x, **kwargs):
    a = x[1][1] + kwargs["avg_pos_votes"]
    b = x[1][2] + kwargs["avg_neg_votes"]
    rank = beta.ppf(0.05, a, b)
    return rank


def print_console_and_file(text, file):
    print(text, file=file)
    print(text)


def print_list(
    file_name,
    frag_dict,
    min_year=0,
    max_year=int(sys.argv[2]),
    cutoff=10,
    ranking_func=bayesian_rating,
    max_print=50,
):
    out_file = open(file_name, "w")

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
        if value[0] in [*range(min_year, max_year + 1)] and value[1] >= cutoff:
            if "female" not in findall("\((\w*?)\)", key) and i < max_print:
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
                name_spaces, key, value[0], value[1], ratio
            ),
            file=out_file,
        )


def graph_years(frag_dict, ranking_func=bayesian_rating):
    avg_pos_votes = statistics.mean([item[1][1] for item in frag_dict.items()])
    avg_neg_votes = statistics.mean([item[1][2] for item in frag_dict.items()])

    x = [item[1][0] for item in mens_all_time.items()]
    y = [
        ranking_func(item, avg_pos_votes=avg_pos_votes, avg_neg_votes=avg_neg_votes)
        for item in mens_all_time.items()
    ]

    return x, y


def main():
    driver = Firefox()
    driver.implicitly_wait(10)
    print_list(*get_awards_votes(driver, sys.argv[1]))
    driver.quit()


if __name__ == "__main__":
    main()
