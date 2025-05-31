import os
import sys
import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd

# Add project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

GRAPH_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cache_london/london_safety_score.graphml"))

if not os.path.exists(GRAPH_FILE):
    print(f"Error: GraphML file not found at {GRAPH_FILE}")
    print("Please run `generate_safety_graph.py` first to generate the safety graph.")
    sys.exit(1)

print("Loading London map data...")
try:
    graph = ox.load_graphml(GRAPH_FILE)
    print("Map loaded successfully.")
except Exception as e:
    print(f"Error loading map: {e}")
    sys.exit(1)

def convert_safety_values(graph):
    """Ensure all `safety_score` values are floats"""
    print("\nConverting `safety_score` values to float...")
    converted_count = 0
    for u, v, data in graph.edges(data=True):
        if "safety_score" in data:
            try:
                data["safety_score"] = float(str(data["safety_score"]).replace(",", "").strip())
                converted_count += 1
            except ValueError:
                print(f"Error converting `safety_score` on edge ({u} -> {v}): {repr(data['safety_score'])}")
                data["safety_score"] = 0.0
    print(f"Successfully converted {converted_count} `safety_score` values.")

convert_safety_values(graph)

def get_route(graph, orig, dest, weight="length"):
    orig_node = ox.distance.nearest_nodes(graph, orig[1], orig[0])
    dest_node = ox.distance.nearest_nodes(graph, dest[1], dest[0])

    print(f"\nStart node: {orig_node}, End node: {dest_node}")

    # Select weight function
    if weight == "safety_score":
        weight_fn = lambda u, v, d: d.get("safety_score", 0.0)
    elif weight == "hybrid":
        weight_fn = lambda u, v, d: 0.5 * d.get("length", 1.0) + 0.5 * d.get("safety_score", 0.0)
    else:
        weight_fn = "length"  # Default to shortest path

    try:
        best_path = nx.shortest_path(graph, orig_node, dest_node, weight=weight_fn)
    except Exception as e:
        return {"error": f"Error computing `{weight}` weighted path: {str(e)}"}

    if len(best_path) < 2:
        return {"error": "No valid path found. Try different start or end points."}

    print(f"`{weight}` path node count: {len(best_path)}")

    route_coords = [(float(graph.nodes[n]["y"]), float(graph.nodes[n]["x"])) for n in best_path]
    route_gdf = ox.routing.route_to_gdf(graph, best_path)

    print("\nRoute GeoDataFrame columns:")
    print(route_gdf.columns)

    total_distance = float(route_gdf["length"].sum())
    total_score = float(route_gdf["safety_score"].sum()) if "safety_score" in route_gdf.columns else 0.0

    return {
        "route": route_coords,
        "total_distance_m": total_distance,
        "total_safety_score": total_score
    }

if __name__ == "__main__":
    test_start = (51.5308, -0.1238)  # King's Cross Station
    test_end = (51.5033, -0.1195)    # London Eye

    print("\nTesting Shortest Path...")
    result = get_route(graph, test_start, test_end, weight="length")
    print(result)

    print("\nTesting Safest Path (Based on safety_score)...")
    result = get_route(graph, test_start, test_end, weight="safety_score")
    print(result)

    print("\nTesting Hybrid Path (50% shortest + 50% safety_score)...")
    result = get_route(graph, test_start, test_end, weight="hybrid")
    print(result)
