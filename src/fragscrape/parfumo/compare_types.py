import re

import click
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from fragscrape.parfumo.create_graph import explode_chart_data


def _add_subplot_to_axes(
    ax: Axes, df: pd.DataFrame, fragrance_1: str, fragrance_2: str
) -> None:
    df = df.loc[
        df.index.str.contains(fragrance_1, case=False)
        | df.index.str.contains(fragrance_2, case=False)
    ]
    df = df.loc[:, (df != 0).any(axis=0)]
    pd.plotting.parallel_coordinates(df.reset_index(), "name", ax=ax)


@click.command()
@click.pass_context
def compare_types(ctx):
    config = ctx.obj.get("config")

    nodes_df = pd.read_json(config["parfumo_enrich_results_path"])
    nodes_df["name"] = nodes_df["name"].apply(lambda x: re.sub("\n", " ", x))
    nodes_df = nodes_df.dropna()
    print(f"Nodes: {nodes_df.shape[0]}")

    fragrance_1 = input("Type the name of a fragrance: ")
    fragrance_2 = input("Type the name of a second fragrance: ")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 5))

    type_pivot = explode_chart_data(nodes_df, "type")
    _add_subplot_to_axes(ax1, type_pivot, fragrance_1, fragrance_2)
    occasion_pivot = explode_chart_data(nodes_df, "occasion")
    _add_subplot_to_axes(ax2, occasion_pivot, fragrance_1, fragrance_2)
    season_pivot = explode_chart_data(nodes_df, "season")
    _add_subplot_to_axes(ax3, season_pivot, fragrance_1, fragrance_2)
    audience_pivot = explode_chart_data(nodes_df, "audience")
    _add_subplot_to_axes(ax4, audience_pivot, fragrance_1, fragrance_2)

    plt.show()
