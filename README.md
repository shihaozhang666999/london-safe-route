# London Safe Walking Route API

This project provides a safe walking route planning system for London, integrating real-time geospatial data and risk assessments.

# Project Description

Safety is a critical concern for urban pedestrians, especially during night-time or in unfamiliar areas. This project provides a smart walking navigation system that suggests routes optimized for safety based on crime statistics and street lighting data.

Built with FastAPI for high-performance API services and Docker for seamless deployment, the system leverages OSMnx and NetworkX for geospatial network analysis and route optimization.

## Features
🚶‍♂️ Risk-Aware Routing: Calculates safest walking paths using crime and lighting datasets.

⚡ FastAPI Backend: Lightweight, high-performance Python web framework.

🐳 Dockerized Deployment: Containerized for easy scaling and consistent environments.

🛡️ Health Check Endpoints: Ensures service reliability and monitors API status.

📑 API Documentation: Interactive API docs powered by Swagger (OpenAPI 3.0).

📊 Data-Driven Decision Making: Integrates real-world geospatial and public safety data.

🛠️ Production Ready: Infrastructure designed with PE principles — observability, resilience, scalability in mind.

## Project Structure

```text
London_safe_route_backend_with_API/
├── Back_end_crime_dataset/
│   └── data/                         # Crime dataset (raw)
├── London/
│   ├── cache_london/                  # Cached map data
│   ├── Map_download/                  # Map download and cache
│   │   ├── cache/
│   │   ├── london.graphml
│   │   └── map_download.py
│   ├── router/                        # API routing
│   │   └── route.py
│   ├── safety/                        # Safety score calculations
│   │   ├── __init__.py
│   │   ├── crime_data_loader.py
│   │   ├── crime_types_scanner.py
│   │   ├── crime_weights.py
│   │   └── path_safety.py
│   ├── services/                      # Service layer
│   │   ├── generate_safety_graph.py
│   │   ├── map_service.py
│   │   └── routing.py
│   └── utils/                         # Utility functions
│       └── geo_utils.py
├── app.py                             # FastAPI main app
├── main.py                            # Entry point
├── crime_data.json                    # Processed crime data
├── delete.py                           # Maintenance script
├── Dockerfile                          # Docker config
├── refresh_graph.sh                    # Shell script to refresh graph
├── requirements.txt                    # Python dependencies
└── README.md                            # Documentation
```
## Tech Stack
Programming Language: Python 3.11

Web Framework: FastAPI

Geospatial Tools: OSMnx, NetworkX

Containerization: Docker

Task Automation: Shell scripts for data refresh and deployment

Monitoring: Health check endpoints for system observability

## Quick Start

1. Clone the repository:
    ```
    git clone https://github.com/shihaozhang666999/london-safe-route.git
    ```
2. Build Docker image:
    ```
    docker build -t london-safe-route .
    docker run -p 8000:8000 london-safe-route
    ```

3. Visit the API docs at:
    ```
    http://127.0.0.1:8000/docs
    ```

## Tech Stack
- Python 3.11
- FastAPI
- NetworkX, OSMnx
- Docker

## API Endpoints
Endpoint	Method	Description
/health	GET	Check if API is running
/route	POST	Get safest route between two points
/docs	GET	

Example POST /route request:
{
  "start": "51.5074, -0.1278",
  "end": "51.5155, -0.0922"
}

## Author
[Shihao Zhang](https://github.com/shihaozhang666999)

## Future Improvements
Add real-time crime data integration

Integrate weather and time-of-day risk adjustments

Deploy on cloud (AWS/GCP) with auto-scaling

Add unit tests and CI/CD pipelines for robust production readiness

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.
