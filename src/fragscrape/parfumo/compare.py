import click
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from fragscrape.parfumo.create_graph import load_and_clean


def _add_subplot_to_axes(ax: Axes, df: pd.DataFrame) -> None:
    df = df.loc[:, (df != 0).any(axis=0)]
    pd.plotting.parallel_coordinates(df.reset_index(), "name", ax=ax, colormap="brg")
    for tick in ax.get_xticklabels():
        tick.set_rotation(20)


@click.command()
def compare():
    nodes_df = load_and_clean().set_index("name")

    fragrance_1 = input("Type the name of a fragrance: ")
    fragrance_2 = input("Type the name of a second fragrance: ")
    nodes_df = nodes_df.loc[
        nodes_df.index.str.contains(fragrance_1, case=False)
        | nodes_df.index.str.contains(fragrance_2, case=False)
    ]

    _, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 5))

    type_data = nodes_df[
        [
            "Animal",
            "Aquatic",
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
        ]
    ]
    type_data = type_data[
        sorted(
            type_data.columns,
            key=lambda c: type_data.diff().iloc[1][c],
        )
    ]
    _add_subplot_to_axes(ax1, type_data)

    occasion_data = nodes_df[
        ["Business", "Daily", "Evening", "Leisure", "Night Out", "Sport"]
    ]
    occasion_data = occasion_data[
        sorted(
            occasion_data.columns,
            key=lambda c: occasion_data.diff().iloc[1][c],
        )
    ]
    _add_subplot_to_axes(ax2, occasion_data)

    season_data = nodes_df[["Spring", "Summer", "Fall", "Winter"]]
    season_data = season_data[
        sorted(
            season_data.columns,
            key=lambda c: season_data.diff().iloc[1][c],
        )
    ]
    _add_subplot_to_axes(ax3, season_data)

    audience_data = nodes_df[["Masculine", "Feminine", "Modern", "Classic"]]
    audience_data = audience_data[
        sorted(
            audience_data.columns,
            key=lambda c: audience_data.diff().iloc[1][c],
        )
    ]
    _add_subplot_to_axes(ax4, audience_data)

    for i, ax in enumerate([ax1, ax2, ax3, ax4], start=1):
        ax.set_ybound(lower=-0.01)
        if i < 4:
            ax.get_legend().set_visible(False)

    plt.subplots_adjust(
        left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.4
    )
    plt.show()
