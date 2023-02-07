# Defines functions for creating JSON point, polyline & polygon barriers
import json

def generateBarriers(wkid=None):
    features = []
    # TODO: change well known id of spatial reference if wkid is defined
    return json.dumps(features)

def generatePolygon(objectId=None, name=None):
    polygon = {
        "geometry": {},
        "attributes": {}
    }
    if name:
        polygon['attributes']['Name'] = name
    if objectId:
        polygon['attributes']['ObjectID'] = objectId
    # TODO: implement ability to change costs
    return polygon