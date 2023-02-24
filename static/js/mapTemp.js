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


function convert2Float(num) {
        num = parseFloat(num);
        if (typeof num === 'number' && num % 1 === 0) {
                num = num.toFixed(1)
        }
        return num
}

async function getRoute() {
        var oLat = convert2Float(document.getElementById('originLat').value);
        var oLnt = convert2Float(document.getElementById('originLnt').value);
        var dLat = convert2Float(document.getElementById('destinationLat').value);
        var dLnt = convert2Float(document.getElementById('destinationLnt').value);
        const url = new URL(`/route`, window.location.origin);
        url.pathname += `/${oLat}/${oLnt}/${dLat}/${dLnt}`;
        const response = await fetch(url);
        const data = await response.json();
        var output = document.getElementById('output')
        output.innerHTML = JSON.stringify(data);
}