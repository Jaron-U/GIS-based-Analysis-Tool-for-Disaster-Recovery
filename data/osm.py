# Fetch Building from OpenStreetMaps via the Overpass API
import requests

OVERPASS_API = "http://overpass-api.de/api/interpreter"

def changeAPI(endpoint: str) -> None:
    """Changes API endpoint with overpass instance"""
    global OVERPASS_API
    OVERPASS_API = endpoint

def queryOverpass(overpass_query: str):
    """Sends Overpass QL query to API"""
    osm_data = requests.get(OVERPASS_API, params={'data': overpass_query})
    return osm_data.json()

