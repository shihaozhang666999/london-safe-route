import os
import pickle
import pandas as pd
import logging
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "../cache_london")
DATA_FOLDER = os.path.join(BASE_DIR, "../../Back_end_crime_dataset/data/UK_crime_data")
CACHE_PATH = os.path.join(CACHE_DIR, "crime_type_data_london.pkl")
CRIME_TYPE_LIST_CACHE = os.path.join(CACHE_DIR, "crime_type_list_london.pkl")

os.makedirs(CACHE_DIR, exist_ok=True)

# Reusable default structure
def default_crime_dict():
    return defaultdict(int)

class CrimeDataLoaderLondon:
    def __init__(self, data_folder=DATA_FOLDER):
        self.data_folder = data_folder
        self.crime_data = defaultdict(default_crime_dict)

    def load_crime_data(self):
        """Load London-specific crime data by type"""
        if os.path.exists(CACHE_PATH):
            print("Loading London crime type data from cache...")
            try:
                with open(CACHE_PATH, "rb") as f:
                    self.crime_data = pickle.load(f)
                return
            except Exception:
                logging.warning("Cache corrupted, reloading CSV data...")

        if not os.path.exists(self.data_folder):
            logging.error(f"Path does not exist: {self.data_folder}")
            return

        all_crime_types = set()

        for year_month in sorted(os.listdir(self.data_folder)):
            folder_path = os.path.join(self.data_folder, year_month)
            if not os.path.isdir(folder_path):
                continue

            print(f"Loading data for {year_month}...")
            for file_name in os.listdir(folder_path):
                if not file_name.endswith(".csv"):
                    continue

                file_path = os.path.join(folder_path, file_name)
                try:
                    df = pd.read_csv(file_path, usecols=["Latitude", "Longitude", "Crime type"], encoding="utf-8")
                    df = df[(df["Latitude"].between(51.30, 51.70)) & (df["Longitude"].between(-0.50, 0.30))]

                    for _, row in df.iterrows():
                        lat, lon = round(row["Latitude"], 6), round(row["Longitude"], 6)
                        crime_type = row["Crime type"]
                        if pd.notna(lat) and pd.notna(lon) and pd.notna(crime_type):
                            self.crime_data[(lat, lon)][crime_type] += 1
                            all_crime_types.add(crime_type)

                except Exception as e:
                    logging.error(f"Unable to parse {file_name}: {e}")

        # Convert to regular dict before saving to avoid pickle errors
        simple_crime_data = {k: dict(v) for k, v in self.crime_data.items()}
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(simple_crime_data, f)
        print(f"London crime type data cached at {CACHE_PATH}")

        with open(CRIME_TYPE_LIST_CACHE, "wb") as f:
            pickle.dump(sorted(all_crime_types), f)
        print(f"Detected crime types saved to: {CRIME_TYPE_LIST_CACHE}")

        # Also update internal data using the simplified structure
        self.crime_data = simple_crime_data

    def get_crime_data(self):
        """Return the crime data"""
        return self.crime_data

if __name__ == "__main__":
    loader = CrimeDataLoaderLondon()
    loader.load_crime_data()
    data = loader.get_crime_data()
    print(f"Sample (lat, lon) crime types: {list(data.items())[:2]}")
