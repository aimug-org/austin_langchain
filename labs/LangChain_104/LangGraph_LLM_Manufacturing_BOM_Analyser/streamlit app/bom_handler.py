import os
import pandas as pd
import networkx as nx
import streamlit.components.v1 as components


class BOMGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.sort_id_to_part_number = {}

    def add_part_and_relationship(self, index, row):

        part_number = row["Part Number"]
        sort_id = row["Part ID"]

        self.sort_id_to_part_number[sort_id] = part_number

        related_sort_id = row["Parent ID"]

        related_part_number = self.sort_id_to_part_number.get(related_sort_id)

        node_attrs = {
            "Description": row["Description"],
            "Price": row["Price"],
        }

        # add nodes to the graph if they don't already exist
        if not self.G.has_node(part_number):
            self.G.add_node(part_number, **node_attrs)

        # add edges to map parent to child relationships
        if self.G.has_node(part_number) and self.G.has_node(related_part_number):
            self.G.add_edge(related_part_number, part_number)

    def update_graph_with_bom_data(self, df):

        self.sort_id_to_part_number.clear()

        for index, row in df.iterrows():
            self.add_part_and_relationship(index, row)

    def get_attributes(self, node):
        return self.G.nodes[node]
