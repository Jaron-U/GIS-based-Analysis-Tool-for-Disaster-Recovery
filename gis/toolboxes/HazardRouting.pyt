# -*- coding: utf-8 -*-

import arcpy
import json
import requests
from os import path
from string import printable
from arcgis2geojson import arcgis2geojson

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

        self.origin = arcpy.Parameter(
            displayName='Origin',
            name='origin',
            datatype='GPPoint',
            parameterType ='Required',
            direction='Input'
        )

        self.destination =  arcpy.Parameter(
            displayName='Destination',
            name='destination',
            datatype='GPPoint',
            parameterType ='Required',
            direction='Input'
        )

        self.barriers =  arcpy.Parameter(
            displayName='Barriers',
            name='barriers',
            datatype="GPFeatureLayer",
            parameterType='Optional',
            direction='Input',
            multiValue=True
        )
        self.selected_map = arcpy.Parameter(
            displayName="Selected Map",
            name="map",
            datatype="GPMap",
            parameterType="Required",
            direction="Input"
        )

        self.directions_flag = arcpy.Parameter(
            displayName="Return Directions?",
            name="directions",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )

        self.bounding_box = arcpy.Parameter(
            displayName="Bounding Box",
            name="bounding_box",
            datatype="GPExtent",
            parameterType="Optional",
            direction="Input"
        )

        self.output_name = arcpy.Parameter(
            displayName="Output Layer Name",
            name="output_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        params = [
            self.origin,
            self.destination,
            self.barriers,
            self.selected_map,
            self.directions_flag,
            self.bounding_box,
            self.output_name
        ]

        # Defaults
        self.directions_flag.value = "false"

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
        if barriers != None:
            barriers = barriers[1:-1].split(';')
        map_name = parameters[3].valueAsText
        directions = parameters[4].valueAsText
        bounding_box = parameters[5].valueAsText
        output_layer_name = parameters[6].valueAsText

        # Use arcpy data-access to only include Geometry within the bounding box
        if bounding_box != None:
            bound_lng1, bound_lat1, bound_lng2, bound_lat2, _misc = bounding_box.split(" ")
            bounding_box = arcpy.Extent(bound_lng1, bound_lat1, bound_lng2, bound_lat2, spatial_reference=arcpy.SpatialReference("WGS 1984"))
            messages.addMessage(f"{bound_lng1}, {bound_lat1} : {bound_lng2}, {bound_lat2}")
        
        # messages.addMessage(barriers)

        workspace, dir = path.split(arcpy.env.workspace)
        if not dir.endswith('.gdb'):
            workspace = arcpy.env.workspace

        # access project resources
        proj = arcpy.mp.ArcGISProject("CURRENT")
        arcgis_map = list(filter(lambda map: map.name == map_name, proj.listMaps()))[0]

        # Acquire polygon data from each barrier layer
        polygons = []

        def addPolygon(polygon_esri):
            nonlocal polygons
            polygon_geojson = arcgis2geojson(polygon_esri)
            if polygon_geojson['type'] == 'Polygon':
                polygons.append(polygon_geojson['coordinates'])
            elif polygon_geojson['type'] == 'MultiPolygon':
                polygons += polygon_geojson['coordinates']


        for barrier in barriers:
            cursor = arcpy.da.SearchCursor(barrier, ["SHAPE@", "SHAPE@JSON"], spatial_reference=arcpy.SpatialReference("WGS 1984"))
            for entry in cursor:
                shape = entry[0]
                # Get ESRI JSON
                polygon_json = json.loads(entry[1])
                # Convert ESRI JSON to GeoJSON
                if bounding_box:
                    if not bounding_box.disjoint(shape):
                        addPolygon(polygon_json)
                else:
                    addPolygon(polygon_json)
        data = {
            "coordinates": [[lng1, lat1], [lng2, lat2]],
            "instructions": 'false'
        }

        if len(polygons) > 0:
            data['options']= {"avoid_polygons": {"type": "MultiPolygon", "coordinates": polygons}}
            #messages.addMessage(data["options"]["avoid_polygons"])
        
        # Let's test if the GeoJSON is correct
        #with open(path.join(workspace, "TEST_GEOJSON.geojson"), "w+", encoding="utf-8") as f:
        #    f.write(json.dumps(data['options']['avoid_polygons']))

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
        for char in output_layer_name:
            if char in printable[10:62]:
                output_name += char
        
        # write result as json we can import
        output_json_filename = path.join(workspace, output_name + "_Route.geojson")
        with open(output_json_filename, "w+", encoding="utf-8") as f:
            f.write(json.dumps(geojson_template))
        
        # This final step should load the layer into the map
        route_layer_path = path.join(arcpy.env.workspace, output_name)
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
