import json

import click
import gravis as gv
import networkx as nx


def visualize(net, size_parameter, refresh):
    fig = gv.vis(
        net,
        gravitational_constant=-5000,
        graph_height=600,
        details_height=150,
        show_details=True,
        use_edge_size_normalization=True,
        edge_size_data_source="weight",
        edge_size_factor=0.5,
        use_node_size_normalization=True,
        node_size_data_source=size_parameter,
        show_node_label=True,
        node_label_data_source="short_name",
        show_node_label_border=True,
        show_node_image=False,
    )
    if refresh:
        fig.export_html("index.html", overwrite=True)
    fig.display()


@click.command()
@click.pass_context
@click.option(
    "--size",
    "-s",
    "size_parameter",
    default="effective_size",
    show_default=True,
    help="Which node attribute to use for node size.",
)
@click.option(
    "--refresh-index",
    "-r",
    "refresh",
    default=True,
    show_default=True,
)
def display_graph(ctx, size_parameter, refresh):
    """Open graph data and visualize in web browser."""
    config = ctx.obj.get("config")

    with open(config["parfumo_graph_path"], "r") as f:
        net = nx.node_link_graph(json.load(f), multigraph=False)

    visualize(net, size_parameter, refresh)
