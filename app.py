# Flask server to serve as an API
import data # our custom wrapper for the ArcGIS APIs
from flask import Flask


app = Flask(__name__)

@app.route("/")
def index():
	return "<p>Hello, World!</p>"

# TODO ADD ROUTE FOR GETTING DIRECTIONS FROM STOPS GIVEN GEOJSON PARAMETER
@app.route("/route")
def findRoute():
	pass

# TODO ADD ROUTE FOR CLOSEST FACILITIES
@app.route("/closest")
def closestFacilities():
	pass


