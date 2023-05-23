# Making request to ArcGIS routing service
# Example which will find the directions between two points using
# the ArcGIS route API.

import requests
import json

token = 'AAPKed0344fad75a47759b9659eae86034daRZO9WuLRC0mwoydQIcZg3E41PAlD6vFtpsUi9cHIw2i7IQUmrjtq8aYyrPZgK2tp'

api = "https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?<parameters>"

# set the geojson style
templateDict = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
            ]
        },
        "properties": {}
    }]
}

# setup request parameter
def getResponse(start, end):
    # Documentation on API parameters here: https://developers.arcgis.com/rest/network/api-reference/route-synchronous-service.htm#ESRI_SECTION2_C85EFA22DE5B48F3BE72E629EAB9049B
    parameters = {
        "stops": start + ";" + end,
        "token": token,
        "f": "pjson",
        "returnDirections": "true",
        "directionsLanguage": "en"
    }
    # send API request
    response = requests.get(api, params=parameters)
    return response


def getResponseORS(start, end, hazards):
    polygons = []

    def addPolygon(polygon_geojson):
        nonlocal polygons
        if polygon_geojson['type'] == 'Polygon':
            polygons.append(polygon_geojson['coordinates'])
        elif polygon_geojson['type'] == 'MultiPolygon':
            polygons += polygon_geojson['coordinates']

    for feature in hazards['features']:
        addPolygon(feature['geometry'])

    data = {
        "coordinates": [[start[0], start[1]], [end[0], end[1]]],
        "instructions": 'false'
    }

    if len(polygons) > 0:
        data['options'] = {"avoid_polygons": {
            "type": "MultiPolygon", "coordinates": polygons}}

    response = requests.post('http://146.190.156.72:8080/ors/v2/directions/driving-car/geojson',
                             data=json.dumps(data),
                             headers={
                                 'Content-Type': 'application/json; charset=utf-8',
                                 'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
                             })

    return response


def convertResponse(response):
    response_dict = json.loads(response.text)
    # get the road data we need
    new_coordinates = response_dict['routes']['features'][0]['geometry']['paths'][0]
    geometry = templateDict["features"][0]['geometry']
    # put the road data input the geojson style text
    geometry['coordinates'] = new_coordinates
    dict = templateDict

    return dict

# get route
def route(data):
    start = (data["stops"][0][0], data["stops"][0][1])
    end = (data["stops"][1][0], data["stops"][1][1])
    response = getResponseORS(start, end, data["hazards"])
    if response.status_code == 200:
        route_data = response.json()
        return route_data
    else:
        error_response = {
            "code": response.status_code,
            "Error": response.text
        }
        return error_response

# if user did not input the polygon file, just return the route
def routeWithoutPolygon(data):
    start = "{},{}".format(data["stops"][0][0], data["stops"][0][1])
    end = "{},{}".format(data["stops"][1][0], data["stops"][1][1])
    response = getResponse(start, end)
    if response.status_code == 200:
        route_data = convertResponse(response)
        return route_data
    else:
        error_response = {
            "code": response.status_code,
            "Error": response.text
        }
        return error_response
