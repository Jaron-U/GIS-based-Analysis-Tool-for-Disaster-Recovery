# Flask server to serve as an API
import data # our custom wrapper for the ArcGIS APIs
from flask import Flask, request, jsonify, render_template
import requests
from directionAPI import route

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("temp.html")

# TODO ADD ROUTE FOR GETTING DIRECTIONS FROM STOPS GIVEN GEOJSON PARAMETER
@app.route('/route/submit-data', methods=['POST'])
def findRoute():
    # result = {"origin" : [oLnt, oLat], "destination": [dLnt, dLat]}
    # retrun result
    submit_data = request.get_json()
    stops = submit_data['stops']
    print(stops)
    hazards = submit_data['hazards']
    # Do something with the data...
    # return jsonify({'message': 'Data received successfully!'})\
    fetchDirectionAPI(submit_data)
    return jsonify(submit_data)

def fetchDirectionAPI(submit_data):
    body = {"coordinates": submit_data['stops']}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf624890af928eff9b49d98d2494338b0a8464',
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/geojson', json=body, headers=headers)

    print(call.status_code, call.reason)
    print(call.text)


# TODO ADD ROUTE FOR CLOSEST FACILITIES
@app.route("/closest")
def closestFacilities():
	pass


