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
        coordinates = [(float(lat1), float(lng1)), (float(lat2), float(lng2))]
        barriers = parameters[2].valueAsText
        map_name = parameters[3].valueAsText

        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace

        # access project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]
        barrier_layer = list(filter(lambda layer: layer.name == barriers, arcgis_map.listLayers()))[0]

        # Write as GeoJSON
        arcpy.conversion.FeaturesToJSON(barrier_layer, path.join(workspace, "barrier_layer.geojson"), geoJSON=True, outputToWGS84=True)
        # open the barrier layer
        with open(path.join(workspace, "barrier_layer.geojson"), "r", encoding='utf-8') as f:
            feature_data = json.loads(f.read())
        
        #messages.addMessage(feature_data)

        # Create request for the open-route-service
        polygons = []
        for feature in feature_data['features']:
            if feature['geometry']['type'] == 'Polygon':
                polygons.append(feature['geometry']['coordinates'])
        
        data = {
            "coordinates": [[lng1, lat1], [lng2, lat2]],
            "instructions": 'false'
        }

        if len(polygons) > 0:
            data['options']= {"avoid_polygons": {"type": "MultiPolygon", "coordinates": polygons}}
        
        response = requests.post('http://146.190.156.72:8080/ors/v2/directions/driving-car/geojson', data=json.dumps(data), headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
        })

        if response.status_code != 200:
            messages.addMessage("Recieved non-200 response code from API:")
            messages.addMessage(response.text)
            return

        response_data = response.json()

        if 'error' in response_data:
            messages.addMessage("Error returned from API:")
            messages.addMessage(response_data)
            return

        # write result as json we can import
        output_json_filename = path.join(workspace, barrier_layer.name + "_Route.geojson")
        with open(output_json_filename, "w+", encoding="utf-8") as f:
            f.write(json.dumps(response_data))
        
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
