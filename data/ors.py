import requests
import json

end_point = "http://146.190.156.72:8080/ors/v2/directions/driving-car/geojson"
profile = ""


def testHealth():
    res = requests.get("http://146.190.156.72:8080/ors/v2/health/")
    return res.json()

def findRoutes(start, end, polygons=[], directions=False):
    api = end_point + profile
    data = {
        "coordinates": [start, end],
        "instructions": str(directions).lower()
    }

    if len(polygons) > 0:    
        data['options']= {"avoid_polygons": {"type": "MultiPolygon", "coordinates": polygons}}
    return requests.post(api, data=json.dumps(data), headers={
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
    })



# polygons = []
polygons = []
polygons.append([[[-123.27433471024904,44.56990961140613],[-123.2742830260548,44.572689420707576],[-123.2766475779405,44.571989863487914],[-123.27637623592082,44.57007529912781],[-123.27433471024904,44.56990961140613]]])
polygons.append([[[-123.27802966460087,44.56771285878773],[-123.27802966460087,44.56900157729788],[-123.27978692720444,44.56900157729788],[-123.27978692720444,44.56771285878773],[-123.27802966460087,44.56771285878773]]])

print(testHealth())

start = [-123.27372428515412,44.573962897440026]
end = [-123.27871563276163,44.56683472511035]
response = findRoutes(start, end, polygons)
print(response.status_code)
print(response.text)








