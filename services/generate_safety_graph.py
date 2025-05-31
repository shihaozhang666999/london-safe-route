import os
import sys
import pickle
import time
import networkx as nx
import osmnx as ox
from tqdm import tqdm
from joblib import Parallel, delayed

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..")))

from safety.path_safety import PathSafetyEvaluator

# === Path configuration ===
CACHE_DIR = os.path.join(BASE_DIR, "..", "cache_london")
GRAPH_FILE = os.path.join(BASE_DIR, "..", "Map_download", "london.graphml")
UPDATED_GRAPH_FILE = os.path.join(CACHE_DIR, "london_safety_score.graphml")
CRIME_DATA_FILE = os.path.join(CACHE_DIR, "crime_type_data_london.pkl")

os.makedirs(CACHE_DIR, exist_ok=True)

# === Parallel processing parameters ===
NUM_WORKERS = 16
BATCH_SIZE = 10_000
MAX_SCORE = 300.0  # Can be adjusted based on actual crime score distribution (for normalizing to 0–10)

def load_data():
    if not os.path.exists(GRAPH_FILE):
        print(f"Map file does not exist: {GRAPH_FILE}")
        sys.exit(1)
    if not os.path.exists(CRIME_DATA_FILE):
        print(f"Crime data file does not exist: {CRIME_DATA_FILE}")
        sys.exit(1)

    print("Loading map...")
    graph = ox.load_graphml(GRAPH_FILE)
    print(f"Map loaded. Nodes: {graph.number_of_nodes()}, Edges: {graph.number_of_edges()}")

    print("Loading crime data...")
    with open(CRIME_DATA_FILE, "rb") as f:
        crime_data = pickle.load(f)

    return graph, crime_data

def compute_safety_for_edge(u, v, key, data, graph, evaluator, counter=None):
    lat, lon = None, None

    if "geometry" in data and hasattr(data["geometry"], "xy"):
        lat = data["geometry"].xy[1][0]
        lon = data["geometry"].xy[0][0]
    elif "length" in data:
        lat1, lon1 = graph.nodes[u]["y"], graph.nodes[u]["x"]
        lat2, lon2 = graph.nodes[v]["y"], graph.nodes[v]["x"]
        lat = (lat1 + lat2) / 2
        lon = (lon1 + lon2) / 2

    if lat and lon:
        raw_score = evaluator.find_nearest_weighted_score(lat, lon)
        normalized = evaluator.normalize_score(raw_score, max_score=MAX_SCORE)
        safety_score = round(min(normalized * 10, 10.0), 2)  # Ensure score stays in 0–10 range
    else:
        safety_score = 0.0

    if counter is not None and counter % 1000 == 0:
        print(f"Processed {counter} edges...")

    return (u, v, key, safety_score)

def compute_edge_safety_scores(graph, crime_data):
    evaluator = PathSafetyEvaluator()
    evaluator.build_kdtree(crime_data)

    edge_list = list(graph.edges(keys=True, data=True))
    print(f"\nTotal {len(edge_list)} edges, starting parallel processing...")

    results = []
    for i in range(0, len(edge_list), BATCH_SIZE):
        batch = edge_list[i:i + BATCH_SIZE]
        print(f"Processing edges {i} ~ {i + len(batch)}...")

        batch_result = Parallel(n_jobs=NUM_WORKERS, backend="threading")(
            delayed(compute_safety_for_edge)(u, v, key, data, graph, evaluator, i + idx)
            for idx, (u, v, key, data) in enumerate(batch)
        )

        results.extend(batch_result)

        # Save batch to cache
        batch_file = os.path.join(CACHE_DIR, f"safety_scores_batch_{i}.pkl")
        with open(batch_file, "wb") as f:
            pickle.dump(batch_result, f)
        print(f"Cached: {batch_file}")

    # Write safety scores into the graph
    for u, v, key, score in results:
        graph[u][v][key]["safety_score"] = score

    return graph

def save_graph(graph):
    print(f"\nSaving final graph to: {UPDATED_GRAPH_FILE}")
    ox.save_graphml(graph, UPDATED_GRAPH_FILE)
    print("Save completed.")

def main():
    start = time.time()
    graph, crime_data = load_data()
    graph = compute_edge_safety_scores(graph, crime_data)
    save_graph(graph)
    print(f"\nAll done. Total time: {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    main()
