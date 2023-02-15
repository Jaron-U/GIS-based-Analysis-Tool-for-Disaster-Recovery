# Demo for python API integration for 2/10/23
# OUT OF DATE

# our custom Python Package
from data.route import setEndpoint, setToken, getRoute, fromGeoJSONToESRI, ESRIJsonFromResponse
import json

setToken('API-KEY-HERE')
setEndpoint('https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?')
barriers = {}

# open GeoJSON example polygon generated from # GeoJSON.io
# https://geojson.io/#map=15.14/44.563581/-123.27663
with open("test/campus_polygon.geojson", "r") as geojson_file:
    geojson = geojson_file.read()
    barriers['features'] = fromGeoJSONToESRI(geojson)
    barriers['spatialReference'] = {'wkid': 4326}

# From Valley Library to Reser Stadium
stops = [(-123.27603351026968, 44.56471464062284),(-123.28143008272647,44.55961596569569)]

# Access API
route = getRoute(stops, barrierPolygons=barriers)

# Save result, we can load into ArcGIS Pro to visualize return data
if route.status_code == 200:
    if 'error' in route.json():
        print("API returned an error:", route.json())
        exit(0)
    # esri_data = route.json()
    with open("route.json", "w+") as result:
        result.write(ESRIJsonFromResponse(route.text))
else:
    print("Response code:", route.status_code)
    print(route.text())
