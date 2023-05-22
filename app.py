# Flask server to serve as an API
from flask import Flask, request, jsonify, render_template
from directionAPI import route, routeWithoutPolygon

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("main.html")

@app.route('/route-to-place', methods=['POST'])
def findRoutePlace():
    submit_data = request.get_json()
    if submit_data['hazards']:
        response = route(submit_data)
    else:
        response = routeWithoutPolygon(submit_data)
    return jsonify(response)

@app.route('/route-to-facilities', methods=['POST'])
def findRouteFacilities():
    submit_data = request.get_json()
    response = route(submit_data)
    return jsonify(response)

