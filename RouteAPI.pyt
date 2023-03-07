# -*- coding: utf-8 -*-

import arcpy
import random
from os import path
import requests
import arcgis
from arcgis.gis import GIS
import http
import requests
import datetime
import arcgis
import pandas as pd
import json


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Closest Facilities Toolbox"
        self.alias = "Closest Facilities Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]

class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Closest Facilities Toolbox"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        incidents = arcpy.Parameter(
            displayName="Starting Points (Incidents)",
            name="starting_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        facilities = arcpy.Parameter(
            displayName="Facilities",
            name="facilities",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        map_parameter = arcpy.Parameter(
            displayName="Map",
            name="map",
            datatype="GPMap",
            parameterType="Required",
            direction="Input"
        )

        outputLayer = arcpy.Parameter(
            displayName="Output Layer Name",
            name="output_layer",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        return [incidents, facilities, map_parameter, outputLayer]

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
        incidents = parameters[0].valueAsText
        facilites = parameters[1].valueAsText
        map_name = parameters[2].valueAsText
        output_layer = parameters[3].valueAsText

        # boilerplate to setup project vars
        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace
        
        # get project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]

        # Obtain incidents layer
        messages.addMessage("Finding point layer named  \"" + incidents + "\"")
        incidents_layer_Name = incidents
        if '\\' in incidents:
            incidents_layer_Name = incidents.split('\\')[-1]
        incidents = list(filter(lambda layer: layer.name == incidents_layer_Name, arcgis_map.listLayers()))[0]

        # Obtain facilities layer
        messages.addMessage("Finding point layer named  \"" + facilites + "\"")
        if '\\' in facilites:
            facilities_layer_Name = facilites.split('\\')[-1]
        facilites = list(filter(lambda layer: layer.name == facilities_layer_Name, arcgis_map.listLayers()))[0]


        messages.addMessage("Transforming facilities layer into JSON file")
        arcpy.conversion.FeaturesToJSON(facilites, path.join(workspace, "facilities.json"))
        messages.addMessage("Transforming incidents layer into JSON file")
        arcpy.conversion.FeaturesToJSON(incidents, path.join(workspace, "incidents.json"))

        # Open generated JSON files and read JSON content
        with open(path.join(workspace, "facilities.json"), "r", encoding="utf-8") as facilities_file:
            facilities_data = json.loads(facilities_file.read())

        with open(path.join(workspace, "incidents.json"), "r", encoding="utf-8") as incidents_file:
            incidents_data = json.loads(incidents_file.read())


        # Connect to the closest facility service
        api_key = "AAPK48cecd16fc9346a98e03f65a2cc0fce11Bx8ccleUqMD3VV-P8brDfuj98-nVfe1bj2qY9WrBeKIoohD2Fy3F2aCjaG1STj4"
        arcgis.GIS("https://www.arcgis.com", api_key=api_key)

        # Call the closest facility service
        result = arcgis.network.analysis.find_closest_facilities(facilities=facilities_data,
                                                                incidents=incidents_data,
                                                                number_of_facilities_to_find=2,
                                                                cutoff=5,
                                                                travel_direction="Facility to Incident",
                                                                time_of_day=datetime.datetime.utcnow(),
                                                                time_of_day_usage="Start Time",
                                                                populate_directions=True
                                                                )

        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_colwidth", None)

        output_routes = result.output_routes.sdf
        print("\n-- Output Routes -- \n")
        messages.addMessage(output_routes[["Name", "Total_Minutes", "Total_Miles", "Total_Kilometers"]].to_string(index=False))

        out_directions = result.output_directions.sdf[["RouteName", "Text"]]
        print("\n-- Output Directions -- \n")
        for route_name in out_directions["RouteName"].unique():
            messages.addMessage(f"\n| {route_name} |\n")
            messages.addMessage(out_directions["Text"].to_string(index=False))

        
        # have to do weird json dump/parse to remove weird escpaing FeatureSet object performs.
        json_output = json.dumps(json.loads(result.output_routes.to_json))
        with open(path.join(workspace, "temp_routes.json"), 'w+', encoding='utf-8') as output:
            output.write(json_output)
        
        messages.addMessage("Adding routes to map...")
        # This is kinda hacky but sorta worked for me.  The routes weren't completely generated (probably due to the cutoff parameter)
        arcpy.conversion.JSONToFeatures(path.join(workspace, "temp_routes.json"), path.join(workspace, output_layer))
        arcgis_map.addLayer(path.join(workspace, output_layer)+".shp")
        messages.addMessage("Done!")
        return
        

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    
    # --------------------------------------------------------------------
    # Checks a string if it contains blanks. If it does, get rid of them.
    # --------------------------------------------------------------------
def name_checker(name):
    # If it contains a blank, change the case of the sring to title case (it looks better), and get rid of the blanks
    return name.title().replace(" ", "") if " " in name else name
# --------------------------------------------------------------------
# Checks if a value is an empty string or not.
# If it is, return a default value, else return the original value
# --------------------------------------------------------------------
def analysis_name(parameter, defaultName): 
    return defaultName if parameter == "" or parameter == " " or parameter == "#" else name_checker(parameter)

def random_rgb():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    # Return RGB array with an alpha value of 100.
    # The alpha value dictates the color transparency - we don't wan't any transparency.
    return [r, g, b, 100]

# --------------------------------------------------------------------
# This function converts a non-point feature layer to a point feature layer.
# The first paramter is the non-point feature layer, and the second parameter is the
# directory where the point feature layer will be written to.
# --------------------------------------------------------------------
def feature_to_point(inFeature, outFeature):
    # Get descriptive properties of the feature layer to be converted
    inFeatureDesc = arcpy.Describe(inFeature)

    # If the feature layer is already a point feature, then return the point feature
    if inFeatureDesc.shapeType == "Point":
        return inFeature
    else:
        # Status message
        message("Your input is not a point feature, it will be converted to one in order to continue with the analysis.")

        # Perform the conversion
        arcpy.FeatureToPoint_management(inFeature, outFeature, "INSIDE")
        # Return the directory where the point feature is located
        return outFeature
def message(message):
    arcpy.AddMessage(message)
# Connect to the closest facility service and call it

def field_as_dict(field):
    field_dict = {"name": field.name, "type": field.type, "alias": field.aliasName}
    if field.type == "String":
        field_dict["length"] = field.length
    return field_dict


