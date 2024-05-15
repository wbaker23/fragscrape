import json
import re

import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


class MplColorHelper:
    """Helper class for coloring nodes using a colormap."""

    def __init__(self, cmap_name, start_val, stop_val):
        self.cmap_name = cmap_name
        self.cmap = plt.get_cmap(cmap_name)
        self.norm = mpl.colors.Normalize(vmin=start_val, vmax=stop_val)
        self.scalarMap = mpl.cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgba(self, val):
        return self.scalarMap.to_rgba(val, bytes=True)

    def get_rgb_str(self, val):
        r, g, b, _ = self.get_rgba(val)
        return f"rgb({r},{g},{b})"


def decompose_df(df: pd.DataFrame, label: str, variables: list):
    """Use PCA to decompose a df."""
    pca = PCA()
    temp_df = df.reset_index()

    x_pca = pd.DataFrame(pca.fit_transform(temp_df[variables].values))
    x_pca["name"] = temp_df[label]
    x_pca.set_index("name", inplace=True)

    return x_pca, pca.explained_variance_ratio_


def explode_chart_data(df, chart_name):
    """Convert df with Parfumo chart data into wide-form."""
    # Explode parfumo chart data
    exp_df = df.explode(chart_name)
    exp_df[f"{chart_name}_name"] = exp_df[chart_name].apply(lambda x: x["ct_name"])
    exp_df[f"{chart_name}_votes"] = exp_df[chart_name].apply(lambda x: x["votes"])

    # Pivot exploded df
    pivot = (
        exp_df[["name", f"{chart_name}_name", f"{chart_name}_votes"]]
        .pivot(index="name", columns=f"{chart_name}_name", values=f"{chart_name}_votes")
        .fillna(0)
        .astype(int)
    )

    return pivot


def generate_edges_df(nodes_df):
    """Generate df listing all possible combinations of nodes with distance metrics."""
    type_pivot = explode_chart_data(nodes_df, "type")
    type_cosine_array = cosine_similarity(type_pivot)

    occasion_pivot = explode_chart_data(nodes_df, "occasion")
    occasion_cosine_array = cosine_similarity(occasion_pivot)

    season_pivot = explode_chart_data(nodes_df, "season")
    season_cosine_array = cosine_similarity(season_pivot)

    audience_pivot = explode_chart_data(nodes_df, "audience")
    audience_cosine_array = cosine_similarity(audience_pivot)

    votes_pivot = (
        type_pivot.join(occasion_pivot).join(season_pivot).join(audience_pivot)
    )
    votes_pivot_cosine_array = cosine_similarity(votes_pivot)

    return (
        pd.DataFrame(
            {
                "source": type_pivot.index[i],
                "target": type_pivot.index[j],
                "type_similarity": type_cosine_array[i][j],
                "occasion_similarity": occasion_cosine_array[i][j],
                "season_similarity": season_cosine_array[i][j],
                "audience_similarity": audience_cosine_array[i][j],
                "votes_similarity": votes_pivot_cosine_array[i][j],
            }
            for i in range(0, len(type_cosine_array))
            for j in range(0, i)
        ),
        votes_pivot,
    )


def load_and_clean(filepath: str):
    nodes_df = pd.read_json(filepath)
    nodes_df["name"] = nodes_df["name"].apply(lambda x: re.sub("\n", " ", x))
    nodes_df = nodes_df.dropna()
    print(nodes_df["collection_group"].value_counts())
    nodes_df = nodes_df.loc[
        nodes_df["collection_group"].isin(
            [
                "I have",
                "Miniatures",
                "Decants",
                "Sample Atomizers",
                "Wish List",
                "Watch List",
            ]
        )
    ]
    nodes_df = nodes_df.loc[nodes_df["brand"] != "The Dua Brand / Dua Fragrances"]
    nodes_df = nodes_df.loc[nodes_df["brand"] != "Rasasi"]
    nodes_df = nodes_df.loc[nodes_df["brand"] != "Nasomatto"]
    print(f"Nodes: {nodes_df.shape[0]}", "\n")
    return nodes_df


@click.command()
@click.pass_context
@click.option(
    "--color",
    "-c",
    "color_groups",
    type=click.Choice(["louvain", "collection"]),
    default="louvain",
    show_default=True,
    help="Choose how to color-code graph nodes.",
)
@click.option(
    "--threshold",
    "-th",
    "threshold",
    type=float,
    default=None,
    show_default=True,
    help="Threshold for connection strength to create edges.",
)
def create_graph(ctx, color_groups, threshold):
    """Create networkx-compatible json file containing graph nodes and edges."""
    config = ctx.obj.get("config")

    # Load graph data
    nodes_df = load_and_clean(config["parfumo_enrich_results_path"])

    # Generate edges
    edges_df, votes_pivot = generate_edges_df(nodes_df)

    # Calculate weight by transforming component features and averaging
    component_columns = [
        "type_similarity",
        "occasion_similarity",
        "season_similarity",
        "audience_similarity",
        "votes_similarity",
    ]
    component_weights = [0, 0, 0, 0, 1]
    edges_df["weight"] = edges_df.apply(
        lambda row: np.average(
            row[component_columns],
            weights=component_weights,
        ),
        axis=1,
    )

    print(edges_df.describe(), "\n")

    # Automatically calculate threshold to exclude outliers
    node_weights_df = (
        pd.merge(
            edges_df[["source", "weight"]]
            .groupby("source")
            .max()
            .sort_values("weight"),
            edges_df[["target", "weight"]]
            .groupby("target")
            .max()
            .sort_values("weight"),
            how="outer",
            left_on="source",
            right_on="target",
        )
        .max(axis=1)
        .sort_values()
    )
    threshold = node_weights_df.iloc[0] if threshold is None else threshold
    print(
        f"Weight threshold: {threshold}",
    )
    edges_df = edges_df[edges_df["weight"] >= threshold]
    print(f"Edges: {edges_df.shape[0]}")

    # Create graph
    net = nx.Graph()

    def assign_node_attribute(df, index, attribute_name):
        if attribute_name in df.loc[index]:
            return int(df.loc[index][attribute_name])
        else:
            return 0

    # Add nodes to graph
    nodes_df.set_index("name", inplace=True)
    for index, row in nodes_df.iterrows():
        net.add_node(
            index,
            collection_group=row["collection_group"],
            type_animal=assign_node_attribute(votes_pivot, index, "Animal"),
            type_aquatic=assign_node_attribute(votes_pivot, index, "Aquatic"),
            type_chypre=assign_node_attribute(votes_pivot, index, "Chypre"),
            type_citrus=assign_node_attribute(votes_pivot, index, "Citrus"),
            type_creamy=assign_node_attribute(votes_pivot, index, "Creamy"),
            type_earthy=assign_node_attribute(votes_pivot, index, "Earthy"),
            type_floral=assign_node_attribute(votes_pivot, index, "Floral"),
            type_fougere=assign_node_attribute(votes_pivot, index, "Fougère"),
            type_fresh=assign_node_attribute(votes_pivot, index, "Fresh"),
            type_fruity=assign_node_attribute(votes_pivot, index, "Fruity"),
            type_gourmand=assign_node_attribute(votes_pivot, index, "Gourmand"),
            type_green=assign_node_attribute(votes_pivot, index, "Green"),
            type_leathery=assign_node_attribute(votes_pivot, index, "Leathery"),
            type_oriental=assign_node_attribute(votes_pivot, index, "Oriental"),
            type_powdery=assign_node_attribute(votes_pivot, index, "Powdery"),
            type_resinous=assign_node_attribute(votes_pivot, index, "Resinous"),
            type_smoky=assign_node_attribute(votes_pivot, index, "Smoky"),
            type_spicy=assign_node_attribute(votes_pivot, index, "Spicy"),
            type_sweet=assign_node_attribute(votes_pivot, index, "Sweet"),
            type_synthetic=assign_node_attribute(votes_pivot, index, "Synthetic"),
            type_woody=assign_node_attribute(votes_pivot, index, "Woody"),
            occasion_evening=assign_node_attribute(votes_pivot, index, "Evening"),
            occasion_business=assign_node_attribute(votes_pivot, index, "Business"),
            occasion_night_out=assign_node_attribute(votes_pivot, index, "Night Out"),
            occasion_leisure=assign_node_attribute(votes_pivot, index, "Leisure"),
            occasion_sport=assign_node_attribute(votes_pivot, index, "Sport"),
            occasion_daily=assign_node_attribute(votes_pivot, index, "Daily"),
            season_spring=assign_node_attribute(votes_pivot, index, "Spring"),
            season_summer=assign_node_attribute(votes_pivot, index, "Summer"),
            season_fall=assign_node_attribute(votes_pivot, index, "Fall"),
            season_winter=assign_node_attribute(votes_pivot, index, "Winter"),
            audience_youthful=assign_node_attribute(votes_pivot, index, "Youthful"),
            audience_mature=assign_node_attribute(votes_pivot, index, "Mature"),
            audience_feminine=assign_node_attribute(votes_pivot, index, "Feminine"),
            audience_masculine=assign_node_attribute(votes_pivot, index, "Masculine"),
        )

    # Add edges to graph
    for index, row in edges_df.iterrows():
        src = row["source"]
        dst = row["target"]
        w = row["weight"]
        net.add_edge(src, dst, weight=w)

    print(f"Minimum degree: {min(list(net.degree()), key=lambda x: x[1])}")
    print(f"Zero-degree nodes: {len([n for n in net.degree() if n[1] == 0])}")
    print(f"One-degree nodes: {len([n for n in net.degree() if n[1] == 1])}")
    print(f"Number of connected components: {nx.number_connected_components(net)}")

    # Calculate centrality measures for nodes
    print("Calculating centrality measures...")
    nx.set_node_attributes(net, nx.pagerank(net, weight="weight"), "pagerank")
    nx.set_node_attributes(
        net, nx.betweenness_centrality(net, weight="weight"), "betweenness_centrality"
    )
    nx.set_node_attributes(net, nx.constraint(net, weight="weight"), "constraint")
    nx.set_node_attributes(
        net, nx.effective_size(net, weight="weight"), "effective_size"
    )
    try:
        nx.set_node_attributes(
            net,
            nx.information_centrality(net, weight="weight"),
            "information_centrality",
        )
    except nx.NetworkXError:
        pass
    nx.set_node_attributes(net, nx.degree_centrality(net), "degree_centrality")

    # Find Louvain communities
    communities = nx.community.louvain_communities(net, weight="weight")
    communities = sorted(communities, key=len, reverse=True)
    print(f"Louvain communities: {len(communities)}")

    if color_groups == "louvain":
        # Color code based on Louvain communities
        node_colors = MplColorHelper("rainbow", 0, len(communities) - 1)
        community_colors = {}
        for node in net:
            for i in range(len(communities)):
                if node in communities[i]:
                    community_colors[node] = node_colors.get_rgb_str(i)
        nx.set_node_attributes(net, community_colors, "color")
    elif color_groups == "collection":
        # Color code based on collection group
        collection_group_colors = {
            p["label"]: p["color"] for p in config["parfumo_pages"]
        }
        nodes_df["color"] = nodes_df.apply(
            lambda row: collection_group_colors[row["collection_group"]],
            axis=1,
        )
        nx.set_node_attributes(net, nodes_df["color"].to_dict(), "color")

    # Create shortened node labels and add node details
    for node_id in net.nodes:
        node = net.nodes[node_id]
        node["short_name"] = re.sub(" \\d{4}.*$", "", node_id)
        node["click"] = "<br>".join(
            f"{i[0]} -- {i[1]} -- {i[2]}"
            for i in sorted(
                ((e[0], e[1], e[2]["weight"]) for e in net.edges([node_id], data=True)),
                key=lambda x: x[2],
                reverse=True,
            )
        )

    nx.set_node_attributes(net, nodes_df["image_src"].to_dict(), "image")

    with open(config["parfumo_graph_path"], "w") as f:
        json.dump(nx.node_link_data(net), f)
