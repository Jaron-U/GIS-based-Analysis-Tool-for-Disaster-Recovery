# -*- coding: utf-8 -*-

import arcpy
import json
import requests
from os import path

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = [
            arcpy.Parameter(
                displayName='Origin',
                name='origin',
                datatype='GPPoint',
                parameterType ='Required',
                direction='Input'
            ),
            arcpy.Parameter(
                displayName='Destination',
                name='destination',
                datatype='GPPoint',
                parameterType ='Required',
                direction='Input'
            ),
            arcpy.Parameter(
                displayName='Barriers',
                name='barriers',
                datatype="GPFeatureLayer",
                parameterType='Required',
                direction='Input'
            ),
            arcpy.Parameter(
                displayName="Selected Map",
                name="map",
                datatype="GPMap",
                parameterType="Required",
                direction="Input"
            )
        ]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        lng1, lat1 = parameters[0].valueAsText.split(" ")
        lng2, lat2 = parameters[1].valueAsText.split(" ")
        stops = [(float(lat1), float(lng1)), (float(lat2), float(lng2))]
        barriers = parameters[2].valueAsText
        map_name = parameters[3].valueAsText

        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace

        # access project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]
        barrier_layer = list(filter(lambda layer: layer.name == barriers, arcgis_map.listLayers()))[0]

        # Write as ESRI json
        arcpy.conversion.FeaturesToJSON(barrier_layer, "barrier_layer.json", geoJSON=False, outputToWGS84=True)
        # open the barrier layer
        with open("barrier_layer.json", "r", encoding='utf-8') as f:
            feature_data = json.loads(f.read())
        
        # perform API call

        # Prune relevant JSON
        barriers = {}
        barriers['spatialReference'] = feature_data['spatialReference']
        barriers['features'] = feature_data['features']
        for i in range(len(barriers['features'])):
            barriers['features'][i]['attributes']['BarrierType'] = 0

        stops = ";".join([f'{lat},{lng}' for lat, lng in stops])

        payload = {
            "f": "json",
            "language": "en",
            "startTime": "now",
            "stops": stops,
            "directions": "False",
            "token": "AAPK8a479fab672b48d081aa5c3c4f038f29Kvt0UXxMh1aUW-ZjbAhkuZb7QZ4OVssIZmFsWU-7BEm5OOVa340zm70ABaWr-OFC"
        }

        payload['polygonBarriers'] = json.dumps(barriers)

        response = requests.get("https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?", params=payload)

        if response.status_code != 200:
            messages.addMessage("Recieved non-200 response code from API:")
            messages.addMessage(response.text)
            return

        response_data = response.json()

        if 'error' in response_data:
            messages.addMessage("Error returned from API:")
            messages.addMessage(response_data)
            return

        esri_json = {}
        esri_json['geometryType'] = response_data['routes']['geometryType']
        esri_json['spatialReference'] = response_data['routes']['spatialReference']
        esri_json['features'] = response_data['routes']['features']

        # write result as json we can import
        output_json_filename = path.join(workspace, barrier_layer.name + "_Route.json")
        with open(output_json_filename, "w+", encoding="utf-8") as f:
            f.write(json.dumps(esri_json))
        
        # This final step should load the layer into the map
        route_layer_path = path.join(arcpy.env.workspace, barrier_layer.name+"Route")
        arcpy.conversion.JSONToFeatures(output_json_filename, route_layer_path)
        arcgis_map.addDataFromPath(route_layer_path)
        messages.addMessage("Done!")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
