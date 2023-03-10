'use strict'

document.addEventListener('DOMContentLoaded', bind)

function bind() {
        //make sure bind function just run one time
        document.removeEventListener('DOMContentLoaded', bind);
        //init the map in the html page
        var map = L.map('map').setView([44.5, -123.2], 10);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        
        //submit lister funtion 
        document.getElementById('submit').addEventListener('click', () => {
                        //get the service type
                        var serviceType = document.getElementById('service').value
                        console.log(serviceType)
                        if (serviceType === "place"){
                                getRoute(L, map)
                        }
                })
}

function getContent() {
        var fReader = new FileReader();
        var file = document.getElementById("uploadFile").files[0]
        fReader.readAsText(file);
        fReader.onload = function() {
                var jsonFeature = JSON.parse(fReader.result)
                console.log(jsonFeature)  
                return jsonFeature
        }
}


async function getRoute(L, map) {
        //get location info, and convert them to float type
        var oLat = parseFloat(document.getElementById('originLat').value);
        var oLnt = parseFloat(document.getElementById('originLnt').value);
        var dLat = parseFloat(document.getElementById('destinationLat').value);
        var dLnt = parseFloat(document.getElementById('destinationLnt').value);

        //hard code for test
        oLnt = -123.27898217097302
        oLat = 44.57272617278602
        dLnt = -123.26839325796291
        dLat = 44.56848686030949

        //convert the input data into json type
        const data = {
                stops: [[oLnt,oLat],[dLnt,dLat]],
                hazards: "geojson"
        };

        //fetch the data from backend
        fetch('/route/submit-data', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {
                        'Content-Type': 'application/json'
                }
        })
        .then(response => response.json())
        .then(data => {
                console.log('Success:', data);
                L.geoJSON(data).addTo(map);
        })
        .catch((error) => {
                console.error('Error:', error);
        });
}
