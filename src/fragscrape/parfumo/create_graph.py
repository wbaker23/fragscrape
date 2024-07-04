import json
import re

import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

from fragscrape.parfumo.database import db_connection


class MplColorHelper:
    """Helper class for coloring nodes using a colormap."""

    def __init__(self, cmap_name, start_val, stop_val):
        self.cmap_name = cmap_name
        self.cmap = plt.get_cmap(cmap_name)
        self.norm = mpl.colors.Normalize(vmin=start_val, vmax=stop_val)
        self.scalar_map = mpl.cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgba(self, val):
        return self.scalar_map.to_rgba(val, bytes=True)

    def get_rgb_str(self, val):
        r, g, b, _ = self.get_rgba(val)
        return f"rgb({r},{g},{b})"


def decompose_df(df: pd.DataFrame, label: str, variables: list):
    """Use PCA to decompose a df."""
    pca = PCA()
    temp_df = df.reset_index()

    x_pca = pd.DataFrame(pca.fit_transform(temp_df[variables].values))
    x_pca[label] = temp_df[label]
    x_pca.set_index(label, inplace=True)

    return x_pca, pca.explained_variance_ratio_


def generate_edges_df(nodes_df) -> pd.DataFrame:
    """Generate df listing all possible combinations of nodes with distance metrics."""
    votes_pivot_cosine_array = cosine_similarity(nodes_df)

    return pd.DataFrame(
        {
            "source": nodes_df.index[i],
            "target": nodes_df.index[j],
            "weight": votes_pivot_cosine_array[i][j],
        }
        for i in range(0, len(votes_pivot_cosine_array))
        for j in range(0, i)
    )


@db_connection
def load_votes(connection) -> pd.DataFrame:
    votes = pd.read_sql(sql="SELECT * FROM votes", con=connection)
    votes = (
        votes.pivot(index="link", columns="category", values="votes")
        .fillna(0)
        .astype(int)
        .apply(lambda row: row / row.sum(), axis=1)
    )
    return votes


@db_connection
def load_collection(connection) -> pd.DataFrame:
    collection = pd.read_sql(
        sql="SELECT * FROM collection WHERE collection_group != 'I Had'", con=connection
    ).set_index("link")
    collection["name"] = collection["name"].apply(lambda x: re.sub("\n", " ", x))
    return collection


@db_connection
def load_tops(connection) -> pd.DataFrame:
    tops = pd.read_sql(sql="SELECT * FROM tops", con=connection).set_index("link")
    tops = tops.dropna()
    tops["name"] = tops["name"].apply(lambda x: re.sub("\n", " ", x))
    return tops


def load_and_clean() -> pd.DataFrame:
    # pylint: disable-next=no-value-for-parameter
    votes = load_votes()
    # pylint: disable-next=no-value-for-parameter
    collection = load_collection()
    nodes_df = collection.join(votes)

    print(nodes_df["collection_group"].value_counts())
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
    nodes_df = load_and_clean()

    # Generate edges
    edges_df = generate_edges_df(nodes_df.select_dtypes(include="float64"))
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

    # Add nodes to graph
    for index, row in nodes_df.iterrows():
        net.add_node(
            index,
            name=row["name"],
            collection_group=row["collection_group"],
            wearings=row["wearings"],
            type_animal=row["Animal"],
            type_aquatic=row["Aquatic"],
            # type_chypre=row["Chypre"],
            type_citrus=row["Citrus"],
            type_creamy=row["Creamy"],
            type_earthy=row["Earthy"],
            type_floral=row["Floral"],
            type_fougere=row["Fougère"],
            type_fresh=row["Fresh"],
            type_fruity=row["Fruity"],
            type_gourmand=row["Gourmand"],
            type_green=row["Green"],
            type_leathery=row["Leathery"],
            type_oriental=row["Oriental"],
            type_powdery=row["Powdery"],
            type_resinous=row["Resinous"],
            type_smoky=row["Smoky"],
            type_spicy=row["Spicy"],
            type_sweet=row["Sweet"],
            type_synthetic=row["Synthetic"],
            type_woody=row["Woody"],
            occasion_evening=row["Evening"],
            occasion_business=row["Business"],
            occasion_night_out=row["Night Out"],
            occasion_leisure=row["Leisure"],
            occasion_sport=row["Sport"],
            occasion_daily=row["Daily"],
            season_spring=row["Spring"],
            season_summer=row["Summer"],
            season_fall=row["Fall"],
            season_winter=row["Winter"],
            audience_youthful=row["Youthful"],
            audience_mature=row["Mature"],
            audience_feminine=row["Feminine"],
            audience_masculine=row["Masculine"],
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
            for i, _ in enumerate(communities):
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
        node["short_name"] = re.sub(" \\d{4}.*$", "", node["name"])
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
