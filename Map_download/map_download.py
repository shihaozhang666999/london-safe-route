import osmnx as ox

city_name = "London, England, UK"

graph = ox.graph_from_place(city_name, network_type="all")

graph_filename = "london.graphml"
ox.save_graphml(graph, graph_filename)

print(f"{city_name} map download complete, containing {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges, saved to {graph_filename}")
