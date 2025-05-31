import os
import glob

# Path to your cache folder
cache_folder = os.path.join(os.path.dirname(__file__), "cache_london")

# Delete all batch .pkl files
batch_files = glob.glob(os.path.join(cache_folder, "safety_scores_batch_*.pkl"))
for file in batch_files:
    os.remove(file)
    print(f" Deleted: {os.path.basename(file)}")

# Delete the final .graphml file
graph_file = os.path.join(cache_folder, "london_safety_score.graphml")
if os.path.exists(graph_file):
    os.remove(graph_file)
    print(f" Deleted: {os.path.basename(graph_file)}")

print("Cleanup complete!")
