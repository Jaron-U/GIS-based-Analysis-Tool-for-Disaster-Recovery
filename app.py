# Flask server to serve as an API
import data # our custom wrapper for the ArcGIS APIs
from flask import Flask, request, jsonify, render_template
#import requests
from directionAPI import route

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("main.html")

# TODO ADD ROUTE FOR GETTING DIRECTIONS FROM STOPS GIVEN GEOJSON PARAMETER
@app.route('/route/submit-data', methods=['POST'])
def findRoute():
    submit_data = request.get_json()
    stops = submit_data['stops']
    hazards = submit_data['hazards']
    response = route(submit_data)
    return jsonify(response)

def fetchDirectionAPI(submit_data):
    return


# TODO ADD ROUTE FOR CLOSEST FACILITIES
@app.route("/closest")
def closestFacilities():
	pass


