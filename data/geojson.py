# Code for converting from geojson to esri json specifications
import barriers

def getPolygonBarrierFromGeoJSON(geojson_str):
    """Returns ESRI-compliant dictionary for polygons in geojson_str"""
    polygon_barriers = {}
    polygon_barriers['features'] = fromGeoJSONToESRI(geojson_str)
    polygon_barriers['spatialReference'] = {"wkid": 4326}
    return polygon_barriers

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
        # TODO: depending on attributes in GeoJSON, load parameters into generatePolygonDict
        shape = barriers.generatePolygonDict()
        shape['geometry']['rings'] = feature['geometry']['coordinates']
        # TODO: make sure right-hand rule is obeyed
    geometry.append(shape)
  return geometry


