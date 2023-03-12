# -*- coding: utf-8 -*-

import arcpy
import json
import requests
from os import path
from string import printable

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
                parameterType='Optional',
                direction='Input',
                multiValue=True
            ),
            arcpy.Parameter(
                displayName="Selected Map",
                name="map",
                datatype="GPMap",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Return Directions?",
                name="directions",
                datatype="GPBoolean",
                parameterType="Optional",
                direction="Input"
            )
        ]

        # Defaults

        params[4].value = "false"

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
        barriers = parameters[2].valueAsText.split(';')
        map_name = parameters[3].valueAsText
        directions = parameters[4].valueAsText
        # messages.addMessage(barriers)

        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace

        # access project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]


        # Acquire polygon data from each barrier layer
        polygons = []
        for barrier in barriers:
            messages.addMessage("Finding barrier layer named  \"" + barrier + "\"")
            if '\\' in barrier:
                barrier = barrier.split('\\')[-1]
            barrier_layer = list(filter(lambda layer: layer.name == barrier, arcgis_map.listLayers()))[0]
            messages.addMessage("Converting barrier layer into JSON...")

            # Write as GeoJSON
            arcpy.conversion.FeaturesToJSON(barrier_layer, path.join(workspace, "barrier_layer.geojson"), geoJSON=True, outputToWGS84=True)
            # open the barrier layer
            with open(path.join(workspace, "barrier_layer.geojson"), "r", encoding='utf-8') as f:
                feature_data = json.loads(f.read())
        
            # Create request for the open-route-service
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

        messages.addMessage(response_data)

        if 'error' in response_data:
            messages.addMessage("Error returned from API:")
            messages.addMessage(response_data)
            return

        output_polyline = response_data['features'][0]['geometry']
        # NOTE: Although ESRI docs claim JSONtoFeatures cannot accept LineString, it actually does
        # accept this geometry for GeoJSON.  In fact, changing this to a "Polyline" breaks the parser
        # either due to bad formatting or some strange Arcpy bug.
        output_polyline['type'] = 'LineString'

        # convert to geojson subset that ArcGIS Pro accepts
        geojson_template = {
            "type": "FeatureCollection",
            "features":[{
                "type": "Feature",
                "geometry": output_polyline
            }]
        }

        # ArcGIS Pro doesn't accept layers with names including non-alphabetic characters (for some reason)
        # so we need to "filter out" illegal characters in the layer name.
        output_name = ""
        for char in barrier_layer.name:
            if char in printable[10:62]:
                output_name += char

        
        # write result as json we can import
        output_json_filename = path.join(workspace, output_name + "_Route.geojson")
        with open(output_json_filename, "w+", encoding="utf-8") as f:
            f.write(json.dumps(geojson_template))
        
        # This final step should load the layer into the map
        route_layer_path = path.join(arcpy.env.workspace, output_name+"Route")
        messages.addMessage("Created GeoJSON file at: " + output_json_filename)
        messages.addMessage("Creating feature layer file at: " + route_layer_path)
        arcpy.conversion.JSONToFeatures(output_json_filename, route_layer_path, geometry_type="Polyline")
        arcgis_map.addDataFromPath(route_layer_path)
        messages.addMessage("Done!")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
