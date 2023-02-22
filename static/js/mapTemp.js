'use strict'

document.addEventListener('DOMContentLoaded', bind())

function bind() {
        var map = L.map('map').setView([30, 11], 3);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        document.getElementById('route').addEventListener('submit', 
                getRoute())

        // L.geoJSON(geojsonFeature).addTo(map)
}


function getRoute() {
        console.log(1111)
        var oLat = document.getElementById('originLat').value;
        console.log(oLat)
        console.log(typeof(oLat))
        var oLot = document.getElementById('originLot').value;
        var dLat = document.getElementById('destinationLat').value;
        var dLot = document.getElementById('destinationLot').value;
        const url = new URL(`/route/${oLat}`, window.location.origin);
        // url.pathname += `${oLat}/${oLot}/${dLat}/${dLot}`;
        // url.pathname += `${oLat}`;
        const response = fetch(url);
        const data = response.json();
        console.log(data)
        var output = document.getElementById('output')
        output.innerHTML = JSON.stringify(data);
}