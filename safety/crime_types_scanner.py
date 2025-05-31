import os
import pandas as pd

# Set the path to the crime data directory
DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Back_end_crime_dataset/data/UK_crime_data"))

# Latitude and longitude range for filtering London area
MIN_LAT, MAX_LAT = 51.30, 51.70
MIN_LON, MAX_LON = -0.50, 0.30

all_crime_types = set()

def scan_crime_types():
    for year_month in sorted(os.listdir(DATA_FOLDER)):
        folder_path = os.path.join(DATA_FOLDER, year_month)
        if not os.path.isdir(folder_path):
            continue

        print(f"Scanning {year_month}...")
        for file_name in os.listdir(folder_path):
            if not file_name.endswith(".csv"):
                continue

            file_path = os.path.join(folder_path, file_name)

            try:
                df = pd.read_csv(file_path, usecols=["Latitude", "Longitude", "Crime type"], encoding="utf-8")
                df = df[
                    df["Latitude"].between(MIN_LAT, MAX_LAT) &
                    df["Longitude"].between(MIN_LON, MAX_LON)
                ]

                crime_types = df["Crime type"].dropna().unique()
                all_crime_types.update(crime_types)

            except Exception as e:
                print(f"Failed to process {file_name}: {e}")

    print("\nAll crime types detected in London:")
    for crime in sorted(all_crime_types):
        print(f"- {crime}")

if __name__ == "__main__":
    scan_crime_types()
