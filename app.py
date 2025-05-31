import os
import sys
import uvicorn
import logging
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import networkx as nx
import time

from utils.geo_utils import load_map_graph, ensure_safety_score_float, geocode_location
from services.routing import get_route

# === Initialize FastAPI app with enhanced metadata ===
app = FastAPI(
    title="🚶‍♂️ London Safe Walking API",
    description="""
London Safe Walking API provides optimized walking routes in London based on distance and crime risk.

You can choose:
- **Shortest Path** (minimum distance)
- **Safest Path** (minimum crime exposure)
- **Hybrid Path** (balance between safety and distance)

Data sources:
- [OpenStreetMap](https://www.openstreetmap.org/)
- [UK Police Crime Data](https://data.police.uk/)
    """,
    version="1.0.0",
    contact={
        "name": "London Safe Navigation Team",
        "url": "https://github.com/your-repo",
        "email": "support@london-safe-walk.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# === Enable CORS for frontend access ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Configure basic logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Access log middleware ===
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # in milliseconds

    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    status_code = response.status_code

    logging.info(f"{client_ip} - \"{method} {url}\" {status_code} - {process_time:.2f}ms")

    return response

# === Path configuration (use graph with merged recent crime data) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(BASE_DIR, "cache_london", "london_safety_score_recent.graphml")

# === Global graph object ===
G: nx.MultiDiGraph = None

# === Load graph when FastAPI starts ===
@app.on_event("startup")
def load_graph_on_startup():
    global G
    logging.info("Loading London map data...")
    G = load_map_graph(GRAPH_PATH)
    ensure_safety_score_float(G)
    logging.info("Map loaded successfully.")

# === Root endpoint for testing ===
@app.get("/")
def index():
    return {"message": "London Safe Route API is running"}

# === Health check endpoint ===
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to confirm API is alive.
    """
    return {"status": "ok"}

# === Get routes by place names ===
@app.get("/route")
def get_safe_routes(
    start_place: str = Query(..., description="Start location name (e.g., King's Cross Station)"),
    end_place: str = Query(..., description="End location name (e.g., London Eye)")
) -> Dict:
    start_loc = geocode_location(start_place)
    end_loc = geocode_location(end_place)

    if "error" in start_loc:
        return {"error": f"Start location error: {start_loc['error']}"}
    if "error" in end_loc:
        return {"error": f"End location error: {end_loc['error']}"}

    start_coords = (start_loc["latitude"], start_loc["longitude"])
    end_coords = (end_loc["latitude"], end_loc["longitude"])

    logging.info(f"Calculating routes from {start_place} to {end_place}")
    logging.info(f"Start coords: {start_coords}, End coords: {end_coords}")

    return {
        "shortest": get_route(G, start_coords, end_coords, weight="length"),
        "safest": get_route(G, start_coords, end_coords, weight="safety_score"),
        "hybrid": get_route(G, start_coords, end_coords, weight="hybrid"),
    }

# === Get routes by coordinates ===
@app.get("/route_coords")
def get_safe_routes_by_coords(
    start_lat: float = Query(..., description="Start latitude"),
    start_lon: float = Query(..., description="Start longitude"),
    end_lat: float = Query(..., description="End latitude"),
    end_lon: float = Query(..., description="End longitude"),
) -> Dict:
    start_coords = (start_lat, start_lon)
    end_coords = (end_lat, end_lon)

    logging.info(f"Calculating routes from {start_coords} to {end_coords}")

    return {
        "shortest": get_route(G, start_coords, end_coords, weight="length"),
        "safest": get_route(G, start_coords, end_coords, weight="safety_score"),
        "hybrid": get_route(G, start_coords, end_coords, weight="hybrid"),
    }

# === Run the server (use 0.0.0.0 for LAN access) ===
if __name__ == "__main__":
    uvicorn.run("London.app:app", host="0.0.0.0", port=8000, reload=True)
