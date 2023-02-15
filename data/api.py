# File holding global API config.

# Globals
token = ''
route_endpoint = 'https://utility.arcgis.com/usrsvcs/appservices/9SL1kSqVl46ogIsh/rest/services/World/Route/NAServer/Route_World'
facilities_endpoint = ''


def ping_route():
  """Returns HTTP status code from using default payload from API documentation."""
  # use default payload from documentation
  stops = [(-122.68782,45.51238), (-122.690176,45.522054), (-122.614995,45.526201)]
  response = getRoute(stops)
  return response

def set_token(s):
  global token
  token = s

def set_route_endpoint(api):
  global route_endpoint
  route_endpoint = api

def set_facilities_endpoint(api):
    global facilities_endpoint
    facilities_endpoint = api