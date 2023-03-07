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

        return [pointsParameter, rangeType, minRange, maxRange, mapParameter]

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
        points_layer = parameters[0].valueAsText
        range_type = parameters[1].valueAsText
        min_range = int(parameters[2].valueAsText)
        max_range = int(parameters[3].valueAsText)
        map_name = parameters[4].valueAsText 
        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace
        
        # get project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]
        messages.addMessage("Finding point layer named  \"" + points_layer + "\"")
        if '\\' in points_layer:
            points_layer_name = points_layer.split('\\')[-1]
        points_layer = list(filter(lambda layer: layer.name == points_layer_name, arcgis_map.listLayers()))[0]

        # save as geojson
        messages.addMessage(points_layer)
        arcpy.conversion.FeaturesToJSON(points_layer, path.join(workspace, "point_layer.geojson"), geoJSON=True)

        # open the barrier layer
        with open(path.join(workspace, "point_layer.geojson"), 'r', encoding='utf-8') as f:
            feature_data = json.loads(f.read())

        messages.addMesage(feature_data)

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
