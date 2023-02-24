# Flask server to serve as an API
import data # our custom wrapper for the ArcGIS APIs
from flask import Flask, request, jsonify, render_template
import asyncio
from aiohttp import ClientSession

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("temp.html")

# TODO ADD ROUTE FOR GETTING DIRECTIONS FROM STOPS GIVEN GEOJSON PARAMETER
@app.route('/route/<float:oLat>/<float:oLnt>/<float:dLat>/<float:dLnt>')
def findRoute(oLat, oLnt, dLat, dLnt):
    result = {"origin" : [oLnt, oLat], "destination": [dLnt, dLat]}
    return result;

# TODO ADD ROUTE FOR CLOSEST FACILITIES
@app.route("/closest")
def closestFacilities():
	pass


