# Fetch Building from OpenStreetMaps via the Overpass API
# Returns the results as valid GeoJSON

from osm2geojson import json2geojson
from geojson_rewind import rewind
from requests import post
import json

OVERPASS_API = "http://overpass-api.de/api/interpreter"

def changeAPI(endpoint: str):
    """Changes API endpoint with overpass instance"""
    global OVERPASS_API
    OVERPASS_API = endpoint

def queryOverpass(overpass_query: str):
    """Sends Overpass QL query to API"""
    osm_data = post(OVERPASS_API, data=overpass_query)
    if osm_data.status_code == 200:
        return osm_data.text
    raise ConnectionError("Could not send request to overpass: ", )


def lookupByRelId(rel_id: int):
    area_id = rel_id + 3600000000
    ql = f'''[out:json];way(area:{id})["building"~".*"];out geom;'''
    try:
        data = queryOverpass(ql)
        geoJSON = rewind(str(json2geojson(data)))
        return geoJSON
    except ConnectionError as e:
        return {"error": str(e)}


