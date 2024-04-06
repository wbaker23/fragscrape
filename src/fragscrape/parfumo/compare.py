import re

import click
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from fragscrape.parfumo.create_graph import explode_chart_data


def _add_subplot_to_axes(ax: Axes, df: pd.DataFrame) -> None:
    df = df.loc[:, (df != 0).any(axis=0)]
    pd.plotting.parallel_coordinates(df.reset_index(), "name", ax=ax, colormap="brg")
    for tick in ax.get_xticklabels():
        tick.set_rotation(20)


@click.command()
@click.pass_context
def compare(ctx):
    config = ctx.obj.get("config")

    nodes_df = pd.read_json(config["parfumo_enrich_results_path"])
    nodes_df["name"] = nodes_df["name"].apply(lambda x: re.sub("\n", " ", x))
    nodes_df = nodes_df.dropna()
    print(f"Nodes: {nodes_df.shape[0]}")

    fragrance_1 = input("Type the name of a fragrance: ")
    fragrance_2 = input("Type the name of a second fragrance: ")
    nodes_df = nodes_df.loc[
        nodes_df["name"].str.contains(fragrance_1, case=False)
        | nodes_df["name"].str.contains(fragrance_2, case=False)
    ]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 5))

    type_pivot = explode_chart_data(nodes_df, "type")
    type_pivot = type_pivot.apply(lambda row: row / row.sum(), axis=1)
    type_pivot = type_pivot[
        sorted(
            type_pivot.columns,
            key=lambda c: type_pivot.iloc[0][c],
        )
    ]
    _add_subplot_to_axes(ax1, type_pivot)
    ax1.get_legend().set_visible(False)
    ax1.set_ybound(lower=-0.01)

    occasion_pivot = explode_chart_data(nodes_df, "occasion")
    occasion_pivot = occasion_pivot.apply(lambda row: row / row.sum(), axis=1)
    occasion_pivot = occasion_pivot[
        sorted(
            occasion_pivot.columns,
            key=lambda c: occasion_pivot.iloc[0][c],
        )
    ]
    _add_subplot_to_axes(ax2, occasion_pivot)
    ax2.get_legend().set_visible(False)
    ax2.set_ybound(lower=-0.01)

    season_pivot = explode_chart_data(nodes_df, "season")
    season_pivot = season_pivot.apply(lambda row: row / row.sum(), axis=1)
    season_pivot = season_pivot[
        sorted(
            season_pivot.columns,
            key=lambda c: season_pivot.iloc[0][c],
        )
    ]
    _add_subplot_to_axes(ax3, season_pivot)
    ax3.get_legend().set_visible(False)
    ax3.set_ybound(lower=-0.01)

    audience_pivot = explode_chart_data(nodes_df, "audience")
    audience_pivot = audience_pivot.apply(lambda row: row / row.sum(), axis=1)
    audience_pivot = audience_pivot[
        sorted(
            audience_pivot.columns,
            key=lambda c: audience_pivot.iloc[0][c],
        )
    ]
    _add_subplot_to_axes(ax4, audience_pivot)
    ax4.set_ybound(lower=-0.01)

    plt.subplots_adjust(
        left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.4
    )
    plt.show()
