import os
import sys

# Force use of current directory as base to ensure correct import of routing and geo_utils
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..")))

from routing import get_route  # Use routing.py specific to London
from utils.geo_utils import geocode_location
import osmnx as ox
import networkx as nx


class MapService:
    def __init__(self, graph_path):
        """Load the walking network graph"""
        print(f"Loading London map data: {graph_path}")
        self.G = ox.load_graphml(graph_path)
        print(f"Map loaded successfully: {graph_path}")

        # Convert safety_score to float type
        print("Checking 'safety_score' data type...")
        for u, v, data in self.G.edges(data=True):
            if "safety_score" in data:
                try:
                    data["safety_score"] = float(data["safety_score"])
                except ValueError:
                    data["safety_score"] = 0.0
        print("'safety_score' data check completed.")

    def _get_coordinates(self, location):
        """Helper function to geocode a location string into (lat, lon)"""
        coords = geocode_location(location)
        if "error" in coords:
            return None

        return (coords["latitude"], coords["longitude"])

    def get_routes_by_coords(self, start_coords, end_coords):
        """
        Calculate three different paths using coordinates:
          - shortest: The shortest path (minimum length)
          - safest: The safest path (minimum safety_score)
          - hybrid: A balanced path (50% shortest + 50% safest)
        """
        if start_coords is None or end_coords is None:
            return {"error": "Invalid coordinates for start or end point."}

        print(f"\nCalculating routes from {start_coords} to {end_coords}")

        shortest_route = get_route(self.G, start_coords, end_coords, weight="length")
        safest_route = get_route(self.G, start_coords, end_coords, weight="safety_score")
        hybrid_route = get_route(self.G, start_coords, end_coords, weight="hybrid")

        return {
            "shortest": shortest_route,
            "safest": safest_route,
            "hybrid": hybrid_route
        }

    def get_routes(self, start_location, end_location):
        """
        Calculate three different paths using location names:
          - shortest: The shortest path (minimum length)
          - safest: The safest path (minimum safety_score)
          - hybrid: A balanced path (50% shortest + 50% safest)
        """
        start_coords = self._get_coordinates(start_location)
        end_coords = self._get_coordinates(end_location)

        return self.get_routes_by_coords(start_coords, end_coords)


if __name__ == "__main__":
    GRAPH_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cache_london/london_safety_score.graphml"))
    map_service = MapService(GRAPH_FILE)

    # Example: Using location names
    test_start = "King's Cross Station, London, UK"
    test_end = "London Eye, London, UK"
    routes = map_service.get_routes(test_start, test_end)
    print("\nPath calculation result using location names:")
    print(routes)

    # Example: Using coordinates
    coords_start = (51.5308, -0.1238)  # King's Cross Station
    coords_end = (51.5033, -0.1196)    # London Eye
    routes_by_coords = map_service.get_routes_by_coords(coords_start, coords_end)
    print("\nPath calculation result using coordinates:")
    print(routes_by_coords)
