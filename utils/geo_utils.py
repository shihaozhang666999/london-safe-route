import os
import networkx as nx
import osmnx as ox
import geopy


def load_map_graph(graph_path: str) -> nx.MultiDiGraph:
    """
    Load the road network graph from a GraphML file.
    """
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"GraphML file not found: {graph_path}")

    print(f"Loading London map data: {graph_path}")
    graph = ox.load_graphml(graph_path)
    print(f"Map loaded successfully: {graph_path}")
    return graph


def ensure_safety_score_float(graph: nx.MultiDiGraph) -> None:
    """
    Ensure that all edges in the graph have 'safety_score' as float type.
    """
    print("Checking 'safety_score' data type...")
    count = 0
    for u, v, k, data in graph.edges(keys=True, data=True):
        if "safety_score" in data:
            try:
                graph[u][v][k]["safety_score"] = float(data["safety_score"])
                count += 1
            except ValueError:
                graph[u][v][k]["safety_score"] = 0.0
    print(f"'safety_score' data check completed. ({count} values converted)")


def geocode_location(place_name):
    """
    Use the geocoding API to get the latitude and longitude of a place.
    :param place_name: e.g., 'London'
    :return: {'latitude': float, 'longitude': float} or {'error': str}
    """
    geolocator = geopy.geocoders.Nominatim(user_agent="map_service")

    try:
        location = geolocator.geocode(place_name)
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
        else:
            return {"error": f"Unable to find the geographic coordinates for {place_name}"}
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}
