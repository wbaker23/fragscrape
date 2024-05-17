import json

import networkx as nx

if __name__ == "__main__":
    with open("data/parfumo/collection/graph.json", "r") as f:
        graph = json.load(f)
    net = nx.node_link_graph(graph, multigraph=False)

    print(
        set(attributes["collection_group"] for name, attributes in net.nodes(data=True))
    )

    nodes = list(net.nodes(data=True))
    for name, attributes in nodes:
        if attributes["collection_group"] not in [
            "I have",
            "Miniatures",
            "Decants",
            "Sample Atomizers",
        ]:
            net.remove_node(name)

    central_node = "Gucci pour Homme II Gucci 2007 EAU DE TOILETTE"

    node_path_lengths = sorted(
        [
            (node, nx.shortest_path_length(net, central_node, node, "weight"))
            for node in net.nodes()
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    from fragscrape.parfumo.create_graph import MplColorHelper

    node_colors = MplColorHelper(
        "cool_r", node_path_lengths[-1][1], node_path_lengths[0][1]
    )

    nx.set_node_attributes(
        net,
        {
            node: {"color": node_colors.get_rgb_str(weight)}
            for node, weight in node_path_lengths
        },
    )

    from fragscrape.parfumo.display_graph import visualize

    visualize(net, "effective_size", False)
