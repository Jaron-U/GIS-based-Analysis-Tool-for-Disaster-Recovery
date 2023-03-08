'use strict'

document.addEventListener('DOMContentLoaded', bind)

function bind() {
        var map = L.map('map').setView([30, 11], 3);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        document.getElementById('submit').addEventListener('click',
                getRoute)

        // L.geoJSON(geojsonFeature).addTo(map)
}

async function getRoute() {
        var oLat = parseFloat(document.getElementById('originLat').value);
        var oLnt = parseFloat(document.getElementById('originLnt').value);
        var dLat = parseFloat(document.getElementById('destinationLat').value);
        var dLnt = parseFloat(document.getElementById('destinationLnt').value);
        // console.log(typeof(dLat))
        const data = {
                stops: [[oLnt,oLat],[dLnt,dLat]],
                hazards: "geojson"
        };

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
                var output = document.getElementById('output')
                output.innerHTML = JSON.stringify(data);
        })
        .catch((error) => {
                console.error('Error:', error);
        });
}
