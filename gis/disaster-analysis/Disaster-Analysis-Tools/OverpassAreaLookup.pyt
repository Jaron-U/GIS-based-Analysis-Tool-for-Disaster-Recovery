# -*- coding: utf-8 -*-
# Filename: OverpassAreaLookup.pyt
# Info: Creates layer of GeoJSON features from Overpass API

import arcpy
from osm2geojson import json2geojson
from geojson_rewind import rewind
from requests import post
from os import getcwd, path
import json
import importlib


OVERPASS_API = 'https://lz4.overpass-api.de/api/interpreter'

#def getOverpassData(name: str):
#    ql = '''[out:json];area["name"="{name}"];way["building"~".*"](area);out geom;'''
#    query = post(OVERPASS_API, data=ql)
#    if query.status_code == 200:
#        osm_data = query.json()
#        return osm_data
#    return {'empty': True}

def getOverpassData(id: int):
    #ql = f'''[out:json];way(area:{id})["building"~".*"];out geom;'''
    # sanity test
    ql = '[out:json];way(area:3605969826)["name"~"Cordley Hall"];out geom;'
    query = post(OVERPASS_API, data=ql)
    if query.status_code == 200:
        return query.text
    return {'empty': True}

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Overpass Area Look-Up"
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
                displayName="OpenStreetMaps Relation ID",
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
        osm_rel_id = int(parameters[0].valueAsText)+3600000000
        arcgis_map = parameters[1].value # should be an ArcGIS Map object
        JSON_data = getOverpassData(osm_rel_id)
        print("Fetched JSON_data of length", len(JSON_data))
        if not 'empty' in JSON_data:
            # We'll potentially need to create a temp file and then delete it.
            # This is because arcpy doesn't understand how to make a non-file-facing
            # interface or API.
            geo_JSON = json2geojson(JSON_data)
            # Create feature class in memory
            filePath = path.join(arcpy.env.workspace, f"{osm_rel_id}.geojson")
            with open(filePath, "w+", encoding='utf-8') as geo_JSON_file:
                geo_JSON_file.write(rewind(json.dumps(geo_JSON)))
            arcpy.conversion.JSONToFeatures(filePath, f"OSM_{arcgis_map}", "polygon")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
