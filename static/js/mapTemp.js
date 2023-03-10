'use strict'

document.addEventListener('DOMContentLoaded', bind)

function bind() {
        document.removeEventListener('DOMContentLoaded', bind);
        console.log("test")
        var map = L.map('map').setView([30, 11], 3);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

  

        document.getElementById('submit').addEventListener('click',
                function(){
                        getRoute(L, map)
                })
}

function sendJSON() {
        fReader = new FileReader();
        
        fileList = this.files;
        console.log(fileList[0]);
        
        fReader.readAsText(fileList[0]);
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
        getContent().then(function(data) {
                console.log(data)  
                L.geoJSON(data).addTo(map); 
        })

        var oLat = parseFloat(document.getElementById('originLat').value);
        var oLnt = parseFloat(document.getElementById('originLnt').value);
        var dLat = parseFloat(document.getElementById('destinationLat').value);
        var dLnt = parseFloat(document.getElementById('destinationLnt').value);

        oLnt = -123.27898217097302
        oLat = 44.57272617278602
        dLnt = -123.26839325796291
        dLat = 44.56848686030949

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
                // console.log('Success:', data);
                L.geoJSON(data).addTo(map);
                // map.fitBounds(group.getRoute)
        })
        .catch((error) => {
                console.error('Error:', error);
        });
}
