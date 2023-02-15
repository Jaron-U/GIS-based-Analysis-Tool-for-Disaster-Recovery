# ArcGIS Pro Routing Service API wrapper
import requests
import json



def _sendRequest(endpoint, params):
  """Sends HTTP GET request to endpoint with parameters dictionary"""
  global token
  payload = params
  payload['token'] = token
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


def ESRIJsonFromResponse(response_text):
  res = json.loads(response_text)
  esri_json = {}
  esri_json['geometryType'] = res['routes']['geometryType']
  esri_json['spatialReference'] = res['routes']['spatialReference']
  esri_json['features'] = res['routes']['features']
  return json.dumps(esri_json)


