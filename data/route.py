# ArcGIS Pro Routing Service API wrapper
import requests
import json

# module-wide variables
token = ''
route_endpoint = 'https://utility.arcgis.com/usrsvcs/appservices/9SL1kSqVl46ogIsh/rest/services/World/Route/NAServer/Route_World'

def ping():
  """Returns HTTP status code from using default payload from API documentation."""
  # use default payload from documentation
  stops = [(-122.68782,45.51238), (-122.690176,45.522054), (-122.614995,45.526201)]
  response = getRoute(stops)
  return response

def setToken(s):
  global token
  token = s

def setEndpoint(api):
  global route_endpoint
  route_endpoint = api

def _sendRequest(endpoint, params):
  """Sends HTTP GET request to endpoint with parameters dictionary"""
  global token
  payload = params
  payload['token'] = token
  print(payload)
  response = requests.get(endpoint, params=payload)
  return response


def listTravelModes():
  # TODO: return list of travel moes
  pass


# Stops should be a list [(lat, lng), (lng,lat)]
# Use: https://www.latlong.net/ as sanity test for longitude/latitude
def getRoute(stops, barrierPolygons=None, startTime="now", directions=False, language="en"):
  """Returns route from A->B"""
  global route_endpoint

  stops = ";".join([f'{lat},{lng}' for lat, lng in stops])

  payload = {
    "f": "json",
    "language": language,
    "startTime": startTime,
    "stops": stops,
    "directions": "False"
  }

  if barrierPolygons:
    # polygon barriers need to be encoded as JSON objects
    payload['polygonBarriers'] = json.dumps(barrierPolygons)

  if directions:
    payload['directions'] = "True"
  
  return _sendRequest(route_endpoint, payload)


#def parseAPIResponse(response: dict):
#  """Given response json dict return trimmed json object ArcGIS Pro can natively import"""
#  data = {}
#  data['routes'][''] = response['features']
#  data['']


def fromESRIToGeoJson(ersi_response):
  """Given ESRI JSON string, return GeoJSON FeatureCollection"""
  response_dict = json.loads(ersi_response)
  templateDict = {
    "type": "FeatureCollection",
    "features": [{
      "type": "Feature",
      "geometry": {
          "type": "LineString",
          "coordinates": []
      },
      "properties": {}
    }]
  }
  # get the road data we need
  new_coordinates = response_dict['routes']['features'][0]['geometry']['paths'][0]
  geometry = templateDict["features"][0]['geometry']
  # put the road data input the geojson style text
  geometry['coordinates'] = new_coordinates
  return templateDict


def fromGeoJSONToESRI(geojson: str):
  """Given GeoJSON FeatureCollection string return ArcGIS-api friendly geometry list"""
  geojson = json.loads(geojson)
  # validate geojson text
  if not 'type' in geojson:
    raise KeyError("GeoJSON lacks type attribute")
  if geojson['type'] != 'FeatureCollection':
    raise KeyError(f"Unsupported GeoJSON type '{geojson['type']}'")
  if not 'features' in geojson:
    raise KeyError("GeoJSON FeatureCollection should have \'features\' array")
  # convert geojson -> esri json
  geometry = []
  for feature in geojson['features']:
    if 'geometry' in feature:
      shape = {}
      if feature['geometry']['type'] == 'Polygon':
        shape = {'geometry': {'rings': feature['geometry']['coordinates']}, 'attributes':{"Name":"Barrier","BarrierType":0}}
        # TODO: make sure right-hand rule is obeyed
    geometry.append(shape)
  return geometry

