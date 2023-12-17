import json

import click
import gravis as gv
import networkx as nx


@click.command()
@click.pass_context
def display_graph(ctx):
    """Open graph data and visualize in web browser."""
    config = ctx.obj.get("config")

    with open(config["parfumo_graph_path"], "r") as f:
        net = nx.node_link_graph(json.load(f), multigraph=False)

    fig = gv.vis(
        net,
        graph_height=700,
        use_edge_size_normalization=True,
        edge_size_data_source="weight",
        edge_size_factor=0.5,
        use_node_size_normalization=True,
        node_size_data_source="pagerank",
        show_node_label=True,
        node_label_data_source="short_name",
        show_node_label_border=True,
        gravitational_constant=-20000,
        avoid_overlap=0.01,
        central_gravity=1,
    )
    fig.display()