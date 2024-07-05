import re

import matplotlib.pyplot as plt
import mplcursors
import pandas as pd
import yaml
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

from fragscrape.parfumo.create_graph import load_collection, load_votes


def normalized_rgb(rgb: tuple):
    max_val = max(rgb)
    return (rgb[0] / max_val, rgb[1] / max_val, rgb[2] / max_val)


if __name__ == "__main__":
    # Load data
    df = load_collection().join(load_votes())

    # Reduce to 2 components
    pca = PCA(n_components=2)
    temp_df = df.reset_index()
    x_pca = pd.DataFrame(pca.fit_transform(temp_df[df.columns.to_list()[5:]].values))
    # print(pca.explained_variance_ratio_.cumsum())
    x_pca["link"] = temp_df["link"]
    x_pca.set_index("link", inplace=True)

    # Join to main df
    df = df.join(
        other=pd.DataFrame(
            MinMaxScaler().fit_transform(x_pca),
            index=x_pca.index,
            columns=x_pca.columns,
        ).rename(columns={0: "pca_1", 1: "pca_0"}),
        on="link",
    )

    # Add color to df
    with open("configs/parfumo_collection_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    collection_group_colors = {p["label"]: p["color"] for p in config["parfumo_pages"]}
    df["color"] = df.apply(
        lambda row: collection_group_colors[row["collection_group"]],
        axis=1,
    )
    df["color_eval"] = df["color"].apply(
        lambda x: normalized_rgb(eval(x.replace("rgb", "")))
    )

    # Make scatter plot
    ax = df.plot.scatter(x="pca_0", y="pca_1", c="color_eval", s=30)

    for name in enumerate(df["name"]):
        plt.annotate(
            text=re.sub(r" \d{4}.*$", "", name[1]),
            xy=(df.iloc[name[0]]["pca_0"], df.iloc[name[0]]["pca_1"]),
            fontsize="xx-small",
        )

    cursor = mplcursors.cursor(ax, hover=False)

    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set(text=df[["name"]].iloc[sel.index].to_string())

    plt.axhline(y=0.5, linewidth=0.5, color="k")
    plt.axvline(x=0.5, linewidth=0.5, color="k")

    # Show scatter plot
    plt.show()
