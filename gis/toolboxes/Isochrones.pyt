# -*- coding: utf-8 -*-

import arcpy
from os import path
import requests
import json

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
        pointsParameter = arcpy.Parameter(
            displayName="Points Layer",
            name="points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        rangeType = arcpy.Parameter(
            displayName="Range Type",
            name="range_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        rangeType.filter.type = "ValueList"
        rangeType.filter.list = ["distance", "time"]

        maxRange = arcpy.Parameter(
            displayName="Range Maximum",
            name="range_max",
            datatype="GPLong",
            parameterType="Required",
            direction="Input"
        )

        minRange = arcpy.Parameter(
            displayName="Range Minimum",
            name="range_min",
            datatype="GPLong",
            parameterType="Required",
            direction="Input"
        )

        mapParameter = arcpy.Parameter(
            displayName="Selected Map",
            name="map",
            datatype="GPMap",
            parameterType="Required",
            direction="Input"
        )

        outputLayer = arcpy.Parameter(
            displayName="Output Layer",
            name="output_layer",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        return [pointsParameter, rangeType, minRange, maxRange, mapParameter, outputLayer]

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

        # TODO: Handle the graphical meta-data

        points_layer = parameters[0].valueAsText
        range_type = parameters[1].valueAsText
        min_range = int(parameters[2].valueAsText)
        max_range = int(parameters[3].valueAsText)
        map_name = parameters[4].valueAsText 
        output_layer = parameters[5].valueAsText

        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace
        
        # get project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]

        # Grab all points
        cursor = arcpy.da.SearchCursor(points_layer, ["SHAPE@XY"], spatial_reference=arcpy.SpatialReference("WGS 1984"))
        locations = []
        for centroid in cursor:
            lng, lat = centroid[0]
            locations.append([lng, lat])
        
        # API call

        feature_collection = None
        i = 0
        while i < len(locations):
            messages.addMessage("Collected " + str(i) + " out of " + str(len(locations)) + " points.")
            data = {
                "range": [min_range, max_range],
                "locations": locations[i:i+2],
                "range_type": range_type
            }
            response = requests.post('http://146.190.156.72:8080/ors/v2/isochrones/driving-car/geojson', data=json.dumps(data), headers={
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
            })
            response_data = response.json()
            if 'error' in response_data:
                messages.addMessage("Error Encountered when calculating Isochrones:")
                messages.addMessage(str(response_data))

            if feature_collection == None:
                feature_collection = response_data
            else:
                for feature in response_data['features']:
                    feature_collection['features'].append(feature)
            # Move i up by 2
            i += 2

        
        output_path = path.join(arcpy.env.workspace, output_layer)
        messages.addMessage(output_path)
        messages.addMessage(output_path + ".geojson")
        with open(path.join(workspace, output_layer) + ".geojson", "w+", encoding="utf-8") as f:
            f.write(json.dumps(feature_collection))
        
        arcpy.conversion.JSONToFeatures(path.join(workspace, output_layer) + ".geojson", output_path, geometry_type="Polygon")
        arcgis_map.addDataFromPath(output_path)

        messages.addMessage("Isochrones layer created!")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
