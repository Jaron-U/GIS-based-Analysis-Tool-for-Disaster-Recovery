# ArcGIS Pro Routing Service API wrapper

import requests

# module-wide variables
token = 'YOUR_TOKEN_HERE'
route_endpoint = 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?'

def _sendRequest(endpoint, params):
  """Sends HTTP GET request to endpoint with parameters dictionary"""
  payload = params
  payload['token'] = token
  response = request.get(endpoint, params=payload)
  return response


def listTravelModes():
  # TODO: return list of travel moes
  pass


# Stops should be a list [(lat, lng), (lng,lat)]
# Use: https://www.latlong.net/ as sanity test for longitude/latitude
def getRoute(stops, startTime="now", directions=False, language="en"):
  """Returns route from A->B"""

  stops = ";".join([f'{lat},{lng}' for lat, lng in stops])

  payload = {
    "f": "json",
    "language": language,
    "startTime": startTime
    "stops": stops
  }
  if directions:
    payload['directions'] = "True"

  return _sendRequest(route_endpoint, payload)

def parseESRI():
  pass

def parseGeoJSON():
  pass

