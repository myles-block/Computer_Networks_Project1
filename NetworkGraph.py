import json
import os
import networkx as nx
import matplotlib.pyplot as plt


# Specify the path to your large JSON file
file_path = os.path.join(os.getcwd(), "DarnellIPCollect.json")


# Function to parse large JSON file and create a network graph
def parse_large_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        G = nx.Graph()
        for entry in data:
            source_address = entry["ip_address_host"]
            G.add_node(source_address)
            for item in entry["ip_address_attach"]:
                destination_address = item["ip"]
                G.add_node(destination_address)
                G.add_edge(source_address, destination_address)

        # Draw the network graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_color='black', arrowsize=20)

    plt.title('Network of IP Addresses')
    plt.show()


# Call the function with your file path
parse_large_json(file_path)
