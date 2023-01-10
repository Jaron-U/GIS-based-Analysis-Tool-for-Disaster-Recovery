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
    ql = f'''[out:json];way(area:{id})["building"~".*"];out geom;'''
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
                displayName="Layer Name",
                name="later_name",
                datatype="GPString",
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
        # Uses overpass areas which require id offset of 3600000000
        osm_rel_id = int(parameters[0].valueAsText)+3600000000

        # get ArcGIS Map object
        map_name = parameters[1].valueAsText
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]

        messages.addMessage(f"Fetching OSM data for relation id={osm_rel_id}")
        JSON_data = getOverpassData(osm_rel_id)
        messages.addMessage(f"Fetched {len(JSON_data)} bytes of JSON data.")
        if not 'empty' in JSON_data:
            geo_JSON = json2geojson(JSON_data)

            # Only include Polygon type features (precautionary measure, maybe not needed)
            filtered_features = []
            for index, feat in enumerate(geo_JSON['features']):
                #geo_JSON['features'][index]['properties'] = {}
                if feat['geometry']['type'] == 'Polygon':
                    filtered_features.append(geo_JSON['features'][index])
            geo_JSON['features'] = filtered_features

            # Make sure we're not writing the geojson file within a geodatabase
            # This will result in the JSONToFeatures call failing if our geojson file
            # is within a geodatabase (not sure why)
            workspace, dir = path.split(arcpy.env.workspace)
            if not dir.endswith('.gdb'):
                workspace = arcpy.env.workspace

            # Write GeoJSON to file
            file_name = f"{osm_rel_id}.geojson"
            file_path = path.join(workspace, file_name)
            with open(file_path, "w+", encoding='utf-8') as geo_JSON_file:
                geo_JSON_file.write(rewind(json.dumps(geo_JSON, ensure_ascii=False)))
            
            messages.addMessage("Converting GeoJSON data to Feature Layer File...")
            # Load GeoJSON file as feature layer in ArcGIS Pro
            layer_file_path = path.join(arcpy.env.workspace, parameters[2].valueAsText)
            arcpy.conversion.JSONToFeatures(file_path, layer_file_path, "POLYGON")

            # Attach to Map!
            messages.addMessage("Inserting Feature Layer into map...")
            arcgis_map.addDataFromPath(layer_file_path)

            messages.addMessage("Done!")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
