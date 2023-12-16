import json

import click
import gravis as gv
import networkx as nx


@click.command()
@click.pass_context
def display_graph(ctx):
    config = ctx.obj.get("config")

    with open(config["parfumo_graph_path"], "r") as f:
        net = nx.node_link_graph(json.load(f), multigraph=False)

    # Display visualization
    fig = gv.vis(
        net,
        graph_height=700,
        use_edge_size_normalization=True,
        edge_size_data_source="weight",
        use_node_size_normalization=True,
        node_size_data_source="pagerank",
        show_node_label=True,
    )
    fig.display()
