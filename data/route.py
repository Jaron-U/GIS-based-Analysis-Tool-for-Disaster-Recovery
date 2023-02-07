# ArcGIS Pro Routing Service API wrapper

import requests

# module-wide variables
token = 'f4LJ3-kW7SL1Je6dCPaxXmlOcGWWU4kVYHRG8XxVQ60-D1kmf9Sve9gv7QdRWXXRmX0L658PeTor1v3VnyY258UjgSpufj07FtZAembY-ifoRsJ7aZx2MnyuP_dBDOgpXd5nNEj1NQFO7L9BJD496A..'
route_endpoint = 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?'
route_endpoint = 'https://utility.arcgis.com/usrsvcs/appservices/9SL1kSqVl46ogIsh/rest/services/World/Route/NAServer/Route_World'

def ping():
  """Returns HTTP status code from using default payload from API documentation."""
  # use default payload from documentation
  stops = [(-122.68782,45.51238), (-122.690176,45.522054), (-122.614995,45.526201)]
  response = getRoute(stops)
  return response

def setEndpoint(api):
  route_endpoint = api

def _sendRequest(endpoint, params):
  """Sends HTTP GET request to endpoint with parameters dictionary"""
  payload = params
  payload['token'] = token
  response = requests.get(endpoint, params=payload)
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
    "startTime": startTime,
    "stops": stops
  }
  if directions:
    payload['directions'] = "True"

  return _sendRequest(route_endpoint, payload)


def parseESRI():
  pass

def parseGeoJSON():
  pass

