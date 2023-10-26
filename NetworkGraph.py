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

        # Create nodes for each IP address
        for entry in data:
            source_address = entry["ip_address_host"]
            G.add_node(source_address)
            for item in entry["ip_address_attach"]:
                destination_address = item["ip"]
                G.add_node(destination_address)

        # Draw the network graph with arrows
        pos = nx.spring_layout(G, k=0.5, iterations=100)
        plt.figure(figsize=(10, 8))  # Adjust the figure size as needed
        nx.draw_networkx(G, pos, with_labels=True, node_size=10, node_color='skyblue', font_size=2, font_color='black', arrows=False)

        plt.title('Network of IP Addresses')
        plt.show()

# Call the function with your file path
parse_large_json(file_path)
