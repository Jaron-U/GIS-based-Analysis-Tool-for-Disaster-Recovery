from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('temp.html')

@app.route('/<name>')
def test(name=None):
    return render_template('temp.html', name=name)

@app.route('/[<lat>,<lon>]')
def send_data(lat=None, lon=None):
    return "<p> " + lat + ", " + lon + " </p>"
