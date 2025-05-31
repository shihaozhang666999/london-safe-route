import os
import pickle
import logging
from scipy.spatial import KDTree

import os
import sys

# Force add the project root directory to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from safety.crime_weights import get_crime_weights


class PathSafetyEvaluator:
    """Calculate the weighted crime score of a path and normalize it to a safety rating from 1 to 10"""

    def __init__(self, max_crime_distance=500):
        self.max_crime_distance = max_crime_distance  # Query radius (meters)
        self.kdtree = None
        self.crime_data_dict = {}

    def build_kdtree(self, crime_data):
        """
        Build KDTree, crime_data: { (lat, lon): {crime_type: count, ...} }
        """
        if not crime_data:
            logging.warning("No crime data available, KDTree will not be built")
            return
        self.crime_data_dict = crime_data
        self.kdtree = KDTree(list(crime_data.keys()))

    def find_nearest_weighted_score(self, lat, lon):
        """
        Find the nearest crime point to the given location and return its weighted score (not normalized)
        """
        if self.kdtree is None or not self.crime_data_dict:
            return 0.0

        lat, lon = round(lat, 6), round(lon, 6)
        dist, idx = self.kdtree.query([(lat, lon)], k=1)
        idx = int(idx[0])
        nearest_loc = list(self.crime_data_dict.keys())[idx]
        dist = dist[0]

        if dist > self.max_crime_distance:
            return 0.0

        crimes = self.crime_data_dict[nearest_loc]
        weights = get_crime_weights()

        weighted_score = sum(
            count * weights.get(crime_type, 1)
            for crime_type, count in crimes.items()
        )

        # print(f"Query point: ({lat}, {lon}), nearest crime point: {nearest_loc}, distance: {dist:.2f}m, raw score: {weighted_score:.2f}")
        return weighted_score

    def get_total_weighted_score(self, path_coordinates, crime_data):
        """
        Compute the total weighted score across all points on the path (not normalized)
        """
        if not path_coordinates:
            return 0.0

        self.build_kdtree(crime_data)

        total_score = 0.0
        for lat, lon in path_coordinates:
            score = self.find_nearest_weighted_score(lat, lon)
            total_score += score

        return total_score

    def normalize_score(self, raw_score, max_score=300.0):
        """
        Normalize the score to a value between 1 and 10
        """
        norm_score = 1 + min(raw_score / max_score, 1.0) * 9
        return round(norm_score, 2)


# Unit test entry
if __name__ == "__main__":
    path_safety = PathSafetyEvaluator(max_crime_distance=500)

    # Sample path coordinates
    test_path = [
        (51.509865, -0.118092),
        (51.510, -0.119),
        (51.515, -0.120)
    ]

    # Sample crime data
    fake_crime_data = {
        (51.51057, -0.118559): {
            "Violence and sexual offences": 10,
            "Drugs": 2,
        },
        (51.510033, -0.119301): {
            "Theft from the person": 3
        },
        (51.514856, -0.120068): {
            "Robbery": 5,
            "Bicycle theft": 1
        }
    }

    total = path_safety.get_total_weighted_score(test_path, fake_crime_data)
    print(f"\nRaw path score: {total:.2f}")
    print(f"Final normalized safety score (1~10): {path_safety.normalize_score(total)}")
