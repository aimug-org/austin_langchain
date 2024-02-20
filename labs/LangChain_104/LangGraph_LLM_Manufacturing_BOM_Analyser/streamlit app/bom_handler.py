import os
import pandas as pd
import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network


class BOMGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.sort_id_to_part_number = {}

    def add_part_and_relationship(self, index, row, analysis_mode):

        part_number = row["Part Number"]
        sort_id = row["Parent ID"]

        self.sort_id_to_part_number[sort_id] = part_number

        related_sort_id = row["Child ID"]

        related_part_number = self.sort_id_to_part_number.get(related_sort_id)

        node_attrs = {
            "Qty": row["Qty"],
            "Description": row["Description"],
            "Price": row["Price"],
        }

        # add nodes to the graph if they don't already exist
        if not self.G.has_node(part_number):
            self.G.add_node(part_number, **node_attrs)

        # add edges to map parent to child relationships
        if self.G.has_node(part_number) and self.G.has_node(related_part_number):
            self.G.add_edge(related_part_number, part_number)

    def update_graph_with_bom_data(self, df, analysis_mode):

        self.sort_id_to_part_number.clear()

        for index, row in df.iterrows():
            self.add_part_and_relationship(index, row, analysis_mode)

    def get_attributes(self, node):
        return self.G.nodes[node]

    def display_graph(self, graph):
        """
        This function displays the graph using Streamlit.
        """

        # Initiate PyVis network object
        part_net = Network(height="465px", bgcolor="#222222", font_color="white")

        # Take Networkx graph and translate it to a PyVis graph format
        part_net.from_nx(graph)

        # Generate network with specific layout settings
        part_net.repulsion(
            node_distance=420,
            central_gravity=0.33,
            spring_length=110,
            spring_strength=0.10,
            damping=0.95,
        )

        current_dir = os.getcwd()
        path = os.path.join(current_dir, "html_files")

        if not os.path.exists(path):
            os.makedirs(path)

        part_net.save_graph(f"{path}/pyvis_graph.html")
        HtmlFile = open(f"{path}/pyvis_graph.html", "r", encoding="utf-8")

        components.html(HtmlFile.read(), height=435)
