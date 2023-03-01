# -*- coding: utf-8 -*-
import arcpy
import random
import os
import requests
import arcgis
from arcgis.gis import GIS
import http
import requests
import datetime
import arcgis
import json
import pandas as pd


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
        # First parameter
        diaster_type = arcpy.Parameter(displayName="Diaster type",
            name="DiasterT",
            datatype="String",
            parameterType="Optional",
            direction="Input")

        diaster_type.filter.type = "ValueList"
        diaster_type.filter.list = ["Landslides","Tsunami","Earthquake"]

        # Second parameter
        incidents = arcpy.Parameter(displayName="Starting Points (Incidents)",
            # name="StartingP",
            # datatype="DEFeatureClass",
            # parameterType="Optional",
            # direction="Input"
            name='origin',
            datatype='Feature Layer',
            parameterType ='Required',
            direction='Input')
        
        incidents_filter = arcpy.Parameter(displayName="Incidents Filter(disabled)",
            name="IncidentsF",
            datatype="SQL Expression",
            parameterType="Optional",
            direction="Input")
        # set up dependency
        incidents_filter.parameterDependencies = [incidents.name]

        Facilities = arcpy.Parameter(displayName="End Points (Facilities)",
            name='destination',
            datatype='Feature Layer',
            parameterType ='Required',
            direction='Input')

        facilities_filter = arcpy.Parameter(displayName="Facilities Filter(disabled)",
            name="FacilitiesF",
            datatype="SQL Expression",
            parameterType="Optional",
            direction="Input")
        # set up dependency
        facilities_filter.parameterDependencies = [incidents.name]
        

        # 6th
        map1 = arcpy.Parameter(displayName="Hazardous Areas",
            name="map",
            datatype="GPMap",
            parameterType="Required",
            direction="Input")
        
        params = [diaster_type, incidents,incidents_filter, Facilities, facilities_filter, map1]
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
        # ********************************************************************
        # Main Program
        # ********************************************************************
        # ////////////////////////////////////////////////////////////////////
        # Earthquake Simulation
        # ////////////////////////////////////////////////////////////////////
        # --------------------------------------------------------------------
        # Setting directories
        # --------------------------------------------------------------------
        # First, we'll calculate the exceedance probability values of the bridges.
        # Get the current directory of the script; it should look something like the following:
        # {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP\Scripts
    # inputs


        # workspace, dir = path.split(arcpy.env.workspace)
        # if not dir.endswith('.gdb'):
        #     workspace = arcpy.env.workspace
        # # access project resources
        # proj = arcpy.mp.ArcGISProject("CURRENT")
        # arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]
        # barrier_layer = list(filter(lambda layer: layer.name == barriers, arcgis_map.listLayers()))[0]



        # the incidents and 
        incidents = parameters[1].valueAsText
        incidentsWhereClause = parameters[2].valueAsText
        facilities = parameters[3].valueAsText
        facilitiesWhereClause = parameters[4].valueAsText

        messages.addMessage("parameter loaded")
        # creating pathing
        scriptsPath = os.getcwd()
        projectPath = os.path.join(os.path.dirname(scriptsPath), "Projects", "GADEP")
        gadepPath = os.path.join(projectPath, "GADEP.gdb")

        # The path for new feature layers
        incidentsFiltered = os.path.join(gadepPath,"IncidentsFiltered")
        facilitiesFiltered = os.path.join(gadepPath,"FacilitiesFiltered")

        # using sql to filter the feature layers
        arcpy.Select_analysis(incidents, incidentsFiltered, incidentsWhereClause)
        arcpy.Select_analysis(facilities, facilitiesFiltered, facilitiesWhereClause)



        incidents  = incidentsFiltered

        facilities = facilitiesFiltered


        arcpy.conversion.FeaturesToJSON(incidents, "CFGeoJsoFacilities.geojson", geoJSON=True, outputToWGS84=True)
        arcpy.conversion.FeaturesToJSON(incidents, "CFGeoJsonIncidents.geojson", geoJSON=True, outputToWGS84=True)

        with open("CFGeoJson.geojson", "r", encoding='utf-8') as f:
            facilities_data = json.loads(f.read())

        with open("CFGeoJson.geojson", "r", encoding='utf-8') as f:
            incidentgs_data = json.loads(f.read())

        #arcpy.conversion.FeaturesToJSON(facilities, "CFGeoJson.geojson", geoJSON=True, outputToWGS84=True)


        
    






        # perform API call
        # Connect to the closest facility service
        api_key = "AAPK48cecd16fc9346a98e03f65a2cc0fce11Bx8ccleUqMD3VV-P8brDfuj98-nVfe1bj2qY9WrBeKIoohD2Fy3F2aCjaG1STj4"
        arcgis.GIS("https://www.arcgis.com", api_key=api_key)

        # Call the closest facility service
        result = arcgis.network.analysis.find_closest_facilities(facilities=facilities_data,
                                                                incidents=incidentgs_data,
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

        #print_result(result)

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




'''
def print_result(result):
    """Print useful information from the result."""
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
'''


