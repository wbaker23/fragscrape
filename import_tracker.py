import json

import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from fragscrape.parfumo.driver import start_driver


def augment_fragrance_data():
    with open("data/parfumo/collection/fragrance_data.json", "r") as f:
        data = json.load(f)

    wearing_dict = pd.read_json("wearings.json").value_counts("name").to_dict()
    for d in data:
        d["wearings"] = wearing_dict[d["link"]] if d["link"] in wearing_dict else 0

    with open("data/parfumo/collection/fragrance_data.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    data = []

    with start_driver() as driver:
        driver.get("https://www.parfumo.com/assistant/tracker")

        while True:
            for w in driver.find_elements(
                By.XPATH, "//div[@class='col-list']/div[@class='name']"
            ):
                name = w.find_element(By.XPATH, "a").get_attribute("href")
                timestamp = w.find_element(By.XPATH, "div").text
                data.append({"name": name, "timestamp": timestamp})

            button = driver.find_elements(By.XPATH, "//span[@class='dir_text']")[1]
            if button.text == "Next":
                ActionChains(driver).move_to_element(button).click(button).perform()
            else:
                break

    with open("wearings.json", "w") as f:
        json.dump(data, f)

    augment_fragrance_data()
