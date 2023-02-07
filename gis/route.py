# Making request to ArcGIS routing service 
# Example which will find the directions between two points using
# the ArcGIS route API.

import requests
import json

token = 'AAPKed0344fad75a47759b9659eae86034daRZO9WuLRC0mwoydQIcZg3E41PAlD6vFtpsUi9cHIw2i7IQUmrjtq8aYyrPZgK2tp'

# api='https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?'
api="https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?<parameters>"

# setup request parameters 


#set the start point
start = "-123.2737581,44.5739238"
end = "-123.2788905,44.5669322"

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






        # for feature in features:
        #     properties = feature["properties"]
        
    #     dicts = json_data
    # return dicts
 
# def write_json_data(dict):
#     with open('D:/data/china_r.json','w') as r:
#         json.dump(dict,r)

# save results (note: to load into ArcGIS Pro requires some data-cleaning)
if response.status_code == 200:
	response_dict = json.loads(response.text)
	new_coordinates = response_dict['routes']['features'][0]['geometry']['paths'][0]
	dicts = {}
	with open('directions.geojson','r',encoding='utf8') as f:
		json_data = json.load(f)
		geometry = json_data["features"][0]['geometry']
		geometry['coordinates'] = new_coordinates
	with open('d.geojson','w') as r:
		json.dump(json_data,r)


else:
	print("Error: ", response.text)

