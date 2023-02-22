# Flask server to serve as an API
import data # our custom wrapper for the ArcGIS APIs
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("temp.html")

# TODO ADD ROUTE FOR GETTING DIRECTIONS FROM STOPS GIVEN GEOJSON PARAMETER
@app.route('/route/<float:oLat>/<float:oLot>/<float:dLat>/<float:dLot>')
def findRoute(oLat, oLot, dLat, dLot):
    result = oLat, oLot, dLat, dLot
    return str(result)

# TODO ADD ROUTE FOR CLOSEST FACILITIES
@app.route("/closest")
def closestFacilities():
	pass


