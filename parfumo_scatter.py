import re

import matplotlib.pyplot as plt
import mplcursors
import pandas as pd
import yaml
from numpy import unique
from sklearn.cluster import AffinityPropagation
from sklearn.decomposition import PCA

from fragscrape.parfumo.create_graph import MplColorHelper, load_collection, load_votes

COLOR_SOURCE = "clusters"

CATEGORIES = {
    "Type": [
        "Animal",
        "Aquatic",
        "Chypre",
        "Citrus",
        "Creamy",
        "Earthy",
        "Floral",
        "Fougère",
        "Fresh",
        "Fruity",
        "Gourmand",
        "Green",
        "Leathery",
        "Oriental",
        "Powdery",
        "Resinous",
        "Smoky",
        "Spicy",
        "Sweet",
        "Synthetic",
        "Woody",
    ],
    "Style": ["Masculine", "Feminine", "Classic", "Modern"],
    "Occasion": ["Daily", "Sport", "Leisure", "Night Out", "Business", "Evening"],
    "Season": ["Winter", "Spring", "Summer", "Fall"],
}

WEIGHTS = {
    "Type": 1,
    "Style": 1,
    "Occasion": 1,
    "Season": 1,
}


def normalized_rgb(rgb: tuple):
    max_val = max(rgb)
    return (rgb[0] / max_val, rgb[1] / max_val, rgb[2] / max_val)


if __name__ == "__main__":
    # Load data
    df = load_collection().join(load_votes())
    df = df[
        df["collection_group"].isin(
            ["I have", "Miniatures", "Decants", "Sample Atomizers"]
        )
    ]

    df_type = (
        df[CATEGORIES["Type"]].apply(lambda row: row / row.sum(), axis=1)
        * WEIGHTS["Type"]
    )
    df_style = (
        df[CATEGORIES["Style"]].apply(lambda row: row / row.sum(), axis=1)
        * WEIGHTS["Style"]
    )
    df_occasion = (
        df[CATEGORIES["Occasion"]].apply(lambda row: row / row.sum(), axis=1)
        * WEIGHTS["Occasion"]
    )
    df_season = (
        df[CATEGORIES["Season"]].apply(lambda row: row / row.sum(), axis=1)
        * WEIGHTS["Season"]
    )

    df = (
        df[["name", "collection_group"]]
        .join(df_type)
        .join(df_style)
        .join(df_occasion)
        .join(df_season)
    )

    # Assign clusters
    features = df[df.columns[2:]]
    model = AffinityPropagation()
    model.fit(features)
    yhat = model.predict(features)
    clusters = unique(yhat)

    # Reduce to 2 components
    pca = PCA(n_components=2)
    temp_df = df.reset_index()
    x_pca = pd.DataFrame(pca.fit_transform(temp_df[df.columns.to_list()[2:]].values))
    print(f"Explained variance: {pca.explained_variance_ratio_.sum() * 100}%")
    x_pca["link"] = temp_df["link"]
    x_pca.set_index("link", inplace=True)

    # Join to main df
    df = df.join(
        other=x_pca.rename(columns={0: "pca_0", 1: "pca_1"}),
        on="link",
    )
    df["cluster"] = yhat

    # Add color to df
    if COLOR_SOURCE == "collection_groups":
        with open("configs/parfumo_collection_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        collection_group_colors = {
            p["label"]: p["color"] for p in config["parfumo_pages"]
        }
        df["color"] = df.apply(
            lambda row: collection_group_colors[row["collection_group"]],
            axis=1,
        )
        df["color_eval"] = df["color"].apply(
            lambda x: normalized_rgb(eval(x.replace("rgb", "")))
        )
    elif COLOR_SOURCE == "clusters":
        colors = MplColorHelper("rainbow", min(clusters), max(clusters))
        df["color_eval"] = df["cluster"].apply(colors.get_rgb_tuple)
    else:
        print("Must define COLOR_SOURCE.")

    # Make scatter plot
    ax = df.plot.scatter(x="pca_0", y="pca_1", c="color_eval", s=100)

    # Add points to existing axes
    cluster_centers = pca.transform(model.cluster_centers_)
    ax2 = plt.scatter(
        x=cluster_centers[:, 0], y=cluster_centers[:, 1], c="k", marker="x", s=100
    )

    for name in enumerate(df["name"]):
        plt.annotate(
            text=re.sub(r" \d{4}.*$", "", name[1]),
            xy=(df.iloc[name[0]]["pca_0"], df.iloc[name[0]]["pca_1"]),
            fontsize="xx-small",
        )

    cursor = mplcursors.cursor(ax, hover=False)

    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set(
            text=f"{df[['name']].iloc[sel.index].to_string()}\n{df[['cluster']].iloc[sel.index].to_string()}"
        )

    plt.axhline(linewidth=0.5, color="k")
    plt.axvline(linewidth=0.5, color="k")

    # Show scatter plot
    plt.show()
