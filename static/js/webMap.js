'use strict'

// use for receving the file content
var jsonFeature
var facilityRet
var map

document.addEventListener('DOMContentLoaded', bind)

function bind() {
        //make sure bind function just run one time
        document.removeEventListener('DOMContentLoaded', bind);
        //init the map in the html page
        map = L.map('map').setView([44.5, -123.2], 10);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        //control the display contents according to the service type
        document.getElementById('p2dInfo').style.display = "none"
        document.getElementById("service").addEventListener("change", function () {
                var serviceType = document.getElementById("service").value
                if (serviceType == "place") {
                        document.getElementById('p2dInfo').style.display = "none"
                        document.getElementById('p2pInfo').style.display = ""
                }
                if (serviceType == "facility") {
                        document.getElementById('p2pInfo').style.display = "none"
                        document.getElementById('p2dInfo').style.display = ""
                }
        })

        //map click event handling
        map.on('click', mapClick);

        document.getElementById("choosePointOrig").addEventListener('click', function () {
            document.getElementById("choosePointOrig").textContent = "Click where you are...";
            map.on('click', mapClickOrigin);
        });

        document.getElementById("choosePointDest").addEventListener('click', function () {
            document.getElementById("choosePointDest").textContent = "Click where you need to go...";
            map.on('click', mapClickDestination);
        });

        //handle user own-location request
        document.getElementById("getUser").addEventListener('click', function () {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    var lat = document.getElementById('originLat').value = parseFloat(pos.coords.latitude);
                    var lng = document.getElementById('originLnt').value = parseFloat(pos.coords.longitude);
                    setPointOnMap(lat, lng, "origin")
                    // set the map view to the user's location
                    map.setView([lat, lng], 15);
                });
            } else {
                alert("Not supported, sorry!");
            }
        });

        //visualize hazard data on the map when it's added
        document.getElementById("uploadFile").addEventListener("change", function () {
                var fReader = new FileReader();
                var file = document.getElementById("uploadFile").files[0]
                fReader.readAsText(file)
                fReader.onload = function () {
                        jsonFeature = JSON.parse(fReader.result)
                        L.geoJSON(jsonFeature).addTo(map)
                        //map.fitBounds(new L.featureGroup(jsonFeature.features[0].geometry.coordinates[0]).getBounds())
                        console.log(jsonFeature.features[0].geometry.coordinates[0])
                }
        });

        document.getElementById("uploadFacFile").addEventListener("change", function () {
            var fReader = new FileReader();
            var file = document.getElementById("uploadFacFile").files[0]
            fReader.readAsText(file)
            fReader.onload = function () {
                facilityRet = JSON.parse(fReader.result)
                //L.geoJSON(facilityRet).addTo(map)
                //map.fitBounds(new L.featureGroup(jsonFeature.features[0].geometry.coordinates[0]).getBounds())
                //console.log(facilityRet.features[0].geometry.coordinates[0])
            }
        });

        //submit lister funtion 
        document.getElementById('submit').addEventListener('click', () => {
                //get the service type
                var serviceType = document.getElementById('service').value;
                console.log(serviceType)
                if (serviceType === "place") {
                        getRoute(L);
                }
                else if (serviceType === "facility") {
                        getFacility(L);
                }
        })
}

function mapClick(e) {
    //console.log(e.latlng);
}

function mapClickOrigin(e) {
    map.off('click', mapClickOrigin);
    var lat = document.getElementById('originLat').value = parseFloat(e.latlng.lat);
    var lng = document.getElementById('originLnt').value = parseFloat(e.latlng.lng);
    document.getElementById('choosePointOrig').textContent = "Choose from map";
    setPointOnMap(lat, lng, "origin")
}

function mapClickDestination(e) {
    map.off('click', mapClickDestination);
    var lat = document.getElementById('destinationLat').value = parseFloat(e.latlng.lat);
    var lng = document.getElementById('destinationLnt').value = parseFloat(e.latlng.lng);
    document.getElementById('choosePointDest').textContent = "Choose from map";
    setPointOnMap(lat, lng, "destination")
}

//display a point icon after user choosed the point on the map
function setPointOnMap(lat, lng, place){
    var marker
    var content
    // create a custom icon with the desired color
    var greenIcon = L.icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    if (place == "origin") {
        // create a marker at the user's location and add it to the map
        marker = L.marker([lat, lng], {icon: greenIcon}).addTo(map);
        content = "you are here"
    }else {
        marker = L.marker([lat, lng]).addTo(map);
        content = "you want to go here"
    }
    
    // create a popup and set its content
    var popup = L.popup().setLatLng([lat, lng]).setContent(content);
    // bind the popup to the marker and open it
    marker.bindPopup(popup).openPopup();
}

async function getFacility(L) {
    //get location info, and convert them to float type
    var oLat = parseFloat(document.getElementById('originLat').value);
    var oLnt = parseFloat(document.getElementById('originLnt').value);
    var dFacility = document.getElementById('facilityIn').value;

    if (typeof document.getElementById('uploadFacFile').files[0] === 'undefined') {
        console.log("searching for facilities")
        facilityRet = dFacility //Should be a custom json segment here, maybe we'll get to it
    }

    //convert the input data into json type
    const input_data = {
        stops: [[oLnt, oLat]],
        incidents: facilityRet,
        hazards: jsonFeature
    };
    console.log(input_data)

    //fetch the data from backend for facilities
    fetch('/route-to-facilities', {
        method: 'POST',
        body: JSON.stringify(input_data),
        headers: {
            'Content-Type': 'application/json'
        }})
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            L.geoJSON(data.geojson).addTo(map);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

async function getRoute(L) {
        //get location info, and convert them to float type
        var oLat = parseFloat(document.getElementById('originLat').value);
        var oLnt = parseFloat(document.getElementById('originLnt').value);
        var dLat = parseFloat(document.getElementById('destinationLat').value);
        var dLnt = parseFloat(document.getElementById('destinationLnt').value);
        
        //if user did not provide the polygon file, just return the route
        if (jsonFeature == undefined){
                jsonFeature = ""
        }

        //convert the input data into json type
        const input_data = {
                stops: [
                        [oLnt, oLat],
                        [dLnt, dLat]
                ],
                hazards: jsonFeature
        };

        //fetch the data from backend for routes
        fetch('/route-to-place', {
                method: 'POST',
                body: JSON.stringify(input_data),
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