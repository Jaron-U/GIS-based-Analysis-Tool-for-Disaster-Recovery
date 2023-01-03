# -*- coding: utf-8 -*-
# Filename: OverpassAreaLookup.pyt
# Info: Creates layer of GeoJSON features from Overpass API

# Looking up Area by name (gets geometry data)
# [out:json];	
# area[name="Oregon State University"];
# way(area)["building"~".*"];
# out geom;

# Looking up Area by name (gets geometry data)
# [out:json];	
# area[name="Oregon State University"];
# way(area)["building"~".*"];
# out geom;

import arcpy
import requests
from os import getcwd, path

OVERPASS_API = 'https://lz4.overpass-api.de/api/interpreter'

def getOverpassData(name: str):
    ql = '''[out:json];area["name"="{name}"];way["building"~".*"](area);out geom;'''
    query = requests.post(OVERPASS_API, data=ql)
    if query.status_code == 200:
        osm_data = query.json()
        return osm_data
    return {'empty': True}

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
        self.label = "Overpass Area Lookup"
        self.description = "Creates map layer of features from Overpass API"
        self.canRunInBackground = False
        self.category = "DisasterRecovery"

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Takes in an ID from OpenStreetMaps,
        # then produces a map layer of GeoJSON features.
        params = [
            arcpy.Parameter(
                displayName="OpenStreetMaps ID",
                name="osm_id",
                datatype="GPLong",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Selected Map",
                name="map",
                datatype="GPMap",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Feature Layer",
                name="osm_layer",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output"
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
        osm_id = parameters[0].valueAsText
        arcgis_map = parameters[1].value # should be an ArcGIS Map object
        # Create Layer
        # Name will get derived from osm_id for the layer

        # arcpy.management.MakeFeatureLayer

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
