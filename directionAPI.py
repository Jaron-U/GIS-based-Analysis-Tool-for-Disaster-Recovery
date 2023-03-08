# Making request to ArcGIS routing service 
# Example which will find the directions between two points using
# the ArcGIS route API.

import requests
import json

token = 'AAPKed0344fad75a47759b9659eae86034daRZO9WuLRC0mwoydQIcZg3E41PAlD6vFtpsUi9cHIw2i7IQUmrjtq8aYyrPZgK2tp'

# api='https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?'
api="https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?<parameters>"

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

# setup request parameters 
def getResponse(start, end):
	# Documentation on API parameters here: https://developers.arcgis.com/rest/network/api-reference/route-synchronous-service.htm#ESRI_SECTION2_C85EFA22DE5B48F3BE72E629EAB9049B
	parameters = {
		# my house to OSU KEC
		# "stops": "-123.2737581,44.5739238;-123.2788905,44.5669322",
		"stops": start + ";" + end,
		"token": token,
		"f": "pjson",
		"returnDirections": "true",
		"directionsLanguage": "en"
	}
	# send API request
	response = requests.get(api, params=parameters)
	return response

def writeResponse(response, filename):
	response_dict = json.loads(response.text)
	# get the road data we need
	new_coordinates = response_dict['routes']['features'][0]['geometry']['paths'][0]
	geometry = templateDict["features"][0]['geometry']
	# put the road data input the geojson style text
	geometry['coordinates'] = new_coordinates
	dict = templateDict
	# write the formatted json into a file.
	with open(filename,'w') as r:
		json.dump(dict,r)



def route():
    #set the start point
	start = "-122.2737581,44.5739238"
	end = "-123.2788905,44.5669322"
	response = getResponse(start, end)
	if response.status_code == 200:
    	# get the response file
		with open('reponse.json','w') as f:
			f.write(response.text)
		writeResponse(response, 'directions.geojson')
	else:
		print("Error: ", response.text)
