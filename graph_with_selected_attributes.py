import json

import networkx as nx

from fragscrape.parfumo.create_graph import MplColorHelper
from fragscrape.parfumo.display_graph import visualize

# Load graph
with open("data/parfumo/collection/graph.json", "r") as f:
    net = nx.node_link_graph(json.load(f), multigraph=False)

all_columns = [
    "type_animal",
    "type_aquatic",
    "type_chypre",
    "type_citrus",
    "type_creamy",
    "type_earthy",
    "type_floral",
    "type_fougere",
    "type_fresh",
    "type_fruity",
    "type_gourmand",
    "type_green",
    "type_leathery",
    "type_oriental",
    "type_powdery",
    "type_resinous",
    "type_smoky",
    "type_spicy",
    "type_sweet",
    "type_synthetic",
    "type_woody",
    "occasion_evening",
    "occasion_business",
    "occasion_night_out",
    "occasion_leisure",
    "occasion_sport",
    "occasion_daily",
    "season_spring",
    "season_summer",
    "season_fall",
    "season_winter",
    "audience_youthful",
    "audience_mature",
    "audience_feminine",
    "audience_masculine",
]

# Set weights
components = ["season_summer", "type_citrus"]
attributes_dict = {}
for node, attributes in net.nodes(data=True):
    component_total = 0.0
    total = 0.0
    for key, value in attributes.items():
        if key in all_columns:
            total += value
        if key in components:
            component_total += value
    attributes_dict[node] = {
        "total_votes": total,
        "component_mean": component_total / total,
        "click": f"Mean: {component_total / total}",
    }
nx.set_node_attributes(net, attributes_dict)

# Create color map
value_list = sorted(nx.get_node_attributes(net, "component_mean").values())
node_colors = MplColorHelper("Purples", value_list[0], value_list[-1])

# Add colors to nodes
nx.set_node_attributes(
    net,
    {
        node: {
            "color": (
                node_colors.get_rgb_str(attr["component_mean"])
                if attr["collection_group"] in ["Decants", "Sample Atomizers"]
                else "rgb(255,255,255)"
            )
        }
        for node, attr in net.nodes(data=True)
    },
)

visualize(net, "effective_size", False)
