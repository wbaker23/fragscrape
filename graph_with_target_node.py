import json

import networkx as nx

from fragscrape.parfumo.create_graph import MplColorHelper
from fragscrape.parfumo.display_graph import visualize

central_node = "https://www.parfumo.com/Perfumes/Louis_Vuitton/imagination"
path_length = 1

if __name__ == "__main__":
    with open("data/parfumo/collection/graph.json", "r") as f:
        graph = json.load(f)
    net = nx.node_link_graph(graph, multigraph=False)

    node_path_lengths = sorted(
        [
            (node, nx.shortest_path_length(net, central_node, node))
            for node in net.nodes()
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    node_colors = MplColorHelper(
        "cool_r", node_path_lengths[-1][1], node_path_lengths[0][1]
    )

    nx.set_node_attributes(
        net,
        {
            node: {
                "color": (
                    node_colors.get_rgb_str(weight)
                    if weight == path_length
                    else "rgb(255,255,255)"
                )
            }
            for node, weight in node_path_lengths
        },
    )

    visualize(net, "effective_size", False)
