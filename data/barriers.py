# Defines functions for creating JSON point, polyline & polygon barriers
import json


def generatePolygonDict(object_id=None, name=None, barrier_type=0, attr_cost_type=None):
    """returns an python dictionary with barrier polygon attributes but without specified geometry.

    Keyword arguments:
    object_id      -- optimal numeric id
    name           -- optinal string identifier
    barrier_type   -- integer representing type of barrier (0=impassable, 1=scaled cost)
    attr_cost_type -- if barrier_type is 1, how the API should scale distance costs across the barrier.
                      Possible types include: "Attr_TravelTime", "Attr_Miles", "Attr_WalkTime" and more
                      specified in the API documentation: https://developers.arcgis.com/rest/network/api-reference/route-synchronous-service.htm 
    """
    polygon = {
        "geometry": {},
        "attributes": {}
    }
    if name:
        polygon['attributes']['Name'] = name
    if objectId:
        polygon['attributes']['ObjectID'] = object_id
    if cost != 0 and attr_cost_type:
        polygon['attributes']['BarrierType'] = cost
        polygon['attributes']['Attr_TravelTime'] = attr_cost_type
    return polygon