# Making request to ArcGIS routing service 
# Example which will find the directions between two points using
# the ArcGIS route API.

import requests

token = 'YOUR_TOKEN_HERE'

api='https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?'

# setup request parameters 

# Documentation on API parameters here: https://developers.arcgis.com/rest/network/api-reference/route-synchronous-service.htm#ESRI_SECTION2_C85EFA22DE5B48F3BE72E629EAB9049B
parameters = {
	# my house to OSU KEC
	"stops": "-123.2737581,44.5739238;-123.2788905,44.5669322",
	"token": token,
	"f": "pjson",
	"returnDirections": "true",
	"directionsLanguage": "en"
}

# send API request
response = requests.get(api, params=parameters)

# save results (note: to load into ArcGIS Pro requires some data-cleaning)
if response.status_code == 200:
	with open("directions.json", "w+", encoding='utf-8') as f:
		f.write(response.text)
else:
	print("Error: ", response.text)

