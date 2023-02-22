# Flask server to serve as an API
import data # our custom wrapper for the ArcGIS APIs
from flask import Flask
from flask import render_template


app = Flask(__name__)

@app.route("/")
def index():
	return render_template("temp.html")

# TODO ADD ROUTE FOR GETTING DIRECTIONS FROM STOPS GIVEN GEOJSON PARAMETER
@app.route("/route")
def findRoute():
	pass

# TODO ADD ROUTE FOR CLOSEST FACILITIES
@app.route("/closest")
def closestFacilities():
	pass


