'use strict'

document.addEventListener('DOMContentLoaded', bind())

function bind(){
    var map = L.map('map').setView([30, 11], 3);    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    document.getElementById('route').addEventListener('submit', getRoute())

    
//     var geojsonFeature = {
//         "type": "Feature",
//         "properties": {},
//         "geometry": {
//           "type": "LineString",
//           "coordinates": [
//             [-0.09, 51.505],
//             [-0.11, 51.5],
//             [-0.13, 51.49]
//           ]
//         }
//       };
//     L.geoJSON(geojsonFeature).addTo(map)
}


function getRoute() {
        console.log(111)
        const oLat = document.getElementById('originLat').value;
        const oLot = document.getElementById('originLot').value;
        const dLat = document.getElementById('destinationLat').value;
        const dLot = document.getElementById('destinationLot').value;
        fetch(`/route/${oLat}/${oLot}/${dLat}/${dLot}`)
          .then(response => response.text())
          .then(result => {
            const resultElement = document.getElementById('output');
            resultElement.innerText = result;
        });
}