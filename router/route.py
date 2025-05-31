import sys
import os
import osmnx as ox
import networkx as nx
from utils.geo_utils import geocode_location

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class RouteLondonService:
    def __init__(self, graph_path=None):
        """Loading London Walking Map"""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.GRAPH_PATH = graph_path or os.path.join(BASE_DIR, "..", "Map_download", "london.graphml")
        print(f"Loading London Map data: {self.GRAPH_PATH}")

        try:
            self.G = ox.load_graphml(self.GRAPH_PATH)
        except Exception as e:
            raise FileNotFoundError(f"Cannot load London Map data: {self.GRAPH_PATH} | Error: {str(e)}")

    def get_graph_info(self):
        """Return London map basic information"""
        return {
            "number_of_nodes": self.G.number_of_nodes(),
            "number_of_edges": self.G.number_of_edges()
        }

    def get_nearest_node(self, lon, lat):
        """Find the nearest map node"""
        try:
            if lon is None or lat is None:
                raise ValueError("lon, lat cannot be None")
            return ox.distance.nearest_nodes(self.G, lon, lat)
        except Exception as e:
            raise ValueError(f"Cannot find the nearest map node: {lon}, {lat} | Error: {str(e)}")

    def get_route(self, start_location, end_location):
        """Calculate the shortest route in London"""
        try:
            start_result = geocode_location(start_location)
            end_result = geocode_location(end_location)

            if "error" in start_result or "error" in end_result:
                return {"error": "Cannot find Start or End"}

            start_lat, start_lon = start_result["latitude"], start_result["longitude"]
            end_lat, end_lon = end_result["latitude"], end_result["longitude"]

            start_node = self.get_nearest_node(start_lon, start_lat)
            end_node = self.get_nearest_node(end_lon, end_lat)

            shortest_path = nx.shortest_path(self.G, source=start_node, target=end_node, weight='length')

            return {"shortest_path": shortest_path}
        except Exception as e:
            return {"error": f"❌ London Fail route calculation: {str(e)}"}

if __name__ == "__main__":
    route_service = RouteLondonService()
    print(route_service.get_graph_info())

    # Test example: London Eye to British Museum
    print(route_service.get_route("London Eye", "British Museum"))
