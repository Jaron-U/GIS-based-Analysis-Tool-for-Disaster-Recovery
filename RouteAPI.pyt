# -*- coding: utf-8 -*-import arcpyimport randomimport osimport requestsimport arcgisfrom arcgis.gis import GISimport httpimport requestsimport datetimeimport arcgisimport pandas as pdimport jsonclass Toolbox(object):    def __init__(self):        """Define the toolbox (the name of the toolbox is the name of the        .pyt file)."""        self.label = "API Ping"        self.alias = "API Ping"        # List of tool classes associated with this toolbox        self.tools = [Tool]class Tool(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "API Ping"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        param1 = arcpy.Parameter(            displayName="Starting Points (Incidents)",            name="Starting_Points_(Incidents)",            datatype="GPFeatureLayer",            parameterType="Required",            direction="Input")        param2 = arcpy.Parameter(            displayName="Incidnts Filter",            name="Incidnts_Filter",            datatype="GPSQLExpression",            parameterType="Required",            direction="Input")        param3 = arcpy.Parameter(            displayName="X Coordinates",            name="X Coordinates",            datatype="GPDouble",            parameterType="Required",            direction="Input")        param4 = arcpy.Parameter(            displayName="Y Coordinates",            name="Y Coordinates",            datatype="GPDouble",            parameterType="Required",            direction="Input")        param2.parameterDependencies = [param1.name]        params = [param1, param2, param3, param4]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        # ********************************************************************        # Main Program        # ********************************************************************        # ////////////////////////////////////////////////////////////////////        # Earthquake Simulation        # ////////////////////////////////////////////////////////////////////        # --------------------------------------------------------------------        # Setting directories        # --------------------------------------------------------------------        # First, we'll calculate the exceedance probability values of the bridges.        # Get the current directory of the script; it should look something like the following:        # {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP\Scripts    # inputs        incidents = parameters[0].value        messages.addMessage("Feature Layer turned into JSON: ")        i = 0        input_layer = parameters[0].valueAsText        fields = arcpy.ListFields(input_layer)        features = []        with arcpy.da.SearchCursor(incidents, ["SHAPE@JSON"] + [field.name for field in fields]) as cursor:            for row in cursor:                attributes = dict(zip([field.name for field in fields], row))                geometry = json.loads(row[0])                feature = {"attributes": attributes, "geometry": geometry}                features.append(feature)                if i >= 1:                    break        incidents2 = {            "displayFieldName": "",            "fieldAliases": {field.name: field.aliasName for field in fields},            "geometryType": arcpy.Describe(input_layer).shapeType,            "fields": [field_as_dict(field) for field in fields],            "features": features        }        incidents_json = json.dumps(incidents2, indent=4)        #messages.addMessage(incidents_json)        # Get the directory of the script        script_dir = os.path.dirname(os.path.abspath(__file__))        # Define the filename for the JSON file        json_filename = "incidents.json"        # Create the full path to the JSON file        json_path = os.path.join(script_dir, json_filename)        # Write the JSON string to the file        with open(json_path, "w") as json_file:            json_file.write(incidents_json)        # Print a message indicating where the file was saved        messages.addMessage(f"JSON file saved to: {json_path}")                        incidentsWhereClause = parameters[1].valueAsText        scriptsPath = os.getcwd()        projectPath = os.path.join(os.path.dirname(scriptsPath), "GADEP")        gadepPath = os.path.join(projectPath, "GADEP.gdb")        incidents = feature_to_point(incidents, os.path.join(gadepPath, "IncidentsPoints"))        incidentsFiltered = os.path.join(gadepPath,"IncidentsFiltered")        #arcpy.Select_analysis(incidents, incidentsFiltered, incidentsWhereClause)                facilities = {            "displayFieldName": "",            "fieldAliases": {                "OBJECTID": "OBJECTID",                "Address": "Address",                "Name": "Name"            },            "geometryType": "esriGeometryPoint",            "spatialReference": {                "wkid": 2913,                "latestWkid": 2913            },            "fields": [                {                    "name": "OBJECTID",                    "type": "esriFieldTypeOID",                    "alias": "OBJECTID"                },                {                    "name": "Address",                    "type": "esriFieldTypeString",                    "alias": "Address",                    "length": 38                },                {                    "name": "Name",                    "type": "esriFieldTypeString",                    "alias": "Name",                    "length": 255                }            ],            "features": [                {                    "attributes": {                        "OBJECTID": 1,                        "Address": "5247 N LOMBARD ST",                        "Name": "Station 26 - Portsmouth/University Park"                    },                    "geometry": {                        "x": 7633115.8891076148,                        "y": 706174.19192913175                    }                },                {                    "attributes": {                        "OBJECTID": 2,                        "Address": "8720 SW 30TH AVE",                        "Name": "Station 18 - Multnomah Village"                    },                    "geometry": {                        "x": 7635782.5767716467,                        "y": 662289.68700787425                    }                },                {                    "attributes": {                        "OBJECTID": 3,                        "Address": "5211 SE MALL ST",                        "Name": "Station 25 - Woodstock"                    },                    "geometry": {                        "x": 7661431,                        "y": 672359.31266404688                    }                },                {                    "attributes": {                        "OBJECTID": 4,                        "Address": "7134 N MARYLAND AVE",                        "Name": "Station 08 - Kenton"                    },                    "geometry": {                        "x": 7643794.7916666716,                        "y": 703290.38877952099                    }                },                {                    "attributes": {                        "OBJECTID": 5,                        "Address": "511 SW COLLEGE ST",                        "Name": "Station 04 - Portland State University"                    },                    "geometry": {                        "x": 7642550.5,                        "y": 679519.81266404688                    }                },                {                    "attributes": {                        "OBJECTID": 6,                        "Address": "1920 SW SPRING ST",                        "Name": "Station 15 - Portland Heights"                    },                    "geometry": {                        "x": 7638483.5,                        "y": 679335.625                    }                },                {                    "attributes": {                        "OBJECTID": 7,                        "Address": "7205 N ALTA AVE",                        "Name": "Station 22 - St. Johns"                    },                    "geometry": {                        "x": 7624439.8517060429,                        "y": 709314.64632545412                    }                },                {                    "attributes": {                        "OBJECTID": 8,                        "Address": "5540 NE SANDY BLVD",                        "Name": "Station 28 - Rose City/Hollywood"                    },                    "geometry": {                        "x": 7662615.3618766367,                        "y": 690552.35597112775                    }                },                {                    "attributes": {                        "OBJECTID": 9,                        "Address": "1500 SE 122ND AVE",                        "Name": "Station 07 - Mill Park"                    },                    "geometry": {                        "x": 7679927.013779521,                        "y": 679567.30544619262                    }                },                {                    "attributes": {                        "OBJECTID": 10,                        "Address": "2915 SE 13TH PL",                        "Name": "Station 23"                    },                    "geometry": {                        "x": 7650264.7985564321,                        "y": 676428.93766404688                    }                },                {                    "attributes": {                        "OBJECTID": 11,                        "Address": "1905 NE KILLINGSWORTH ST",                        "Name": "Station 14 - Alberta Park"                    },                    "geometry": {                        "x": 7652607.5,                        "y": 698666.18766404688                    }                },                {                    "attributes": {                        "OBJECTID": 12,                        "Address": "3130 NW SKYLINE BLVD",                        "Name": "Station 27 - Forest Heights"                    },                    "geometry": {                        "x": 7622995.1902887076,                        "y": 692838.97867454588                    }                },                {                    "attributes": {                        "OBJECTID": 13,                        "Address": "55 SW ASH ST",                        "Name": " Station 01 - Old Town"                    },                    "geometry": {                        "x": 7645808.7355643064,                        "y": 683815.50524935126                    }                },                {                    "attributes": {                        "OBJECTID": 14,                        "Address": "1715 SW SKYLINE BLVD",                        "Name": "Station 16 - Sylvan"                    },                    "geometry": {                        "x": 7628988.0731627345,                        "y": 680269.33989500999                    }                },                {                    "attributes": {                        "OBJECTID": 15,                        "Address": "3660 NW FRONT AVE",                        "Name": "Station 06 - NW Industrial"                    },                    "geometry": {                        "x": 7637036.8218503892,                        "y": 693920.00656168163                    }                },                {                    "attributes": {                        "OBJECTID": 16,                        "Address": "926 NE WEIDLER ST",                        "Name": " Station 13 - Lloyd District"                    },                    "geometry": {                        "x": 7649727.5,                        "y": 688199.5                    }                },                {                    "attributes": {                        "OBJECTID": 17,                        "Address": "2235 SE BYBEE BLVD",                        "Name": "Station 20 - Sellwood/Moreland"                    },                    "geometry": {                        "x": 7652687.5,                        "y": 666304.5                    }                },                {                    "attributes": {                        "OBJECTID": 18,                        "Address": "848 N TOMAHAWK ISLAND DR",                        "Name": "Station 17 - Hayden Island"                    },                    "geometry": {                        "x": 7645359.5,                        "y": 715887.625                    }                },                {                    "attributes": {                        "OBJECTID": 19,                        "Address": "4515 N MARYLAND AVE",                        "Name": "Station 24 - Overlook/Swan Island"                    },                    "geometry": {                        "x": 7643391.5,                        "y": 696263.31233595312                    }                },                {                    "attributes": {                        "OBJECTID": 20,                        "Address": "13310 SE FOSTER RD",                        "Name": "Station 29 - Powellhurst Fire Station"                    },                    "geometry": {                        "x": 7682355,                        "y": 666334.81266404688                    }                },                {                    "attributes": {                        "OBJECTID": 21,                        "Address": "1505 SW DEWITT ST",                        "Name": "Station 05 - Hillsdale"                    },                    "geometry": {                        "x": 7639618,                        "y": 668875.81266404688                    }                },                {                    "attributes": {                        "OBJECTID": 22,                        "Address": "1706 SE CESAR E CHAVEZ BLVD",                        "Name": "Station 09 - Hawthrone District"                    },                    "geometry": {                        "x": 7658078.427821517,                        "y": 679407.81988188624                    }                },                {                    "attributes": {                        "OBJECTID": 23,                        "Address": "4800 NE 122ND AVE",                        "Name": "Station 02 - Parkrose"                    },                    "geometry": {                        "x": 7680485.5,                        "y": 695991.68766404688                    }                },                {                    "attributes": {                        "OBJECTID": 24,                        "Address": "1715 NW JOHNSON ST",                        "Name": "Station 03 - Northwest Pearl District"                    },                    "geometry": {                        "x": 7641263,                        "y": 686484.06266404688                    }                },                {                    "attributes": {                        "OBJECTID": 25,                        "Address": "8645 NE SANDY BLVD",                        "Name": "Station 12 - Sandy Blvd"                    },                    "geometry": {                        "x": 7670903.9547244161,                        "y": 695130.7529527545                    }                },                {                    "attributes": {                        "OBJECTID": 26,                        "Address": "451 SW TAYLORS FERRY RD",                        "Name": "Station 10 - Burlingame"                    },                    "geometry": {                        "x": 7642023.5,                        "y": 662635.31233595312                    }                },                {                    "attributes": {                        "OBJECTID": 27,                        "Address": "7301 E BURNSIDE ST",                        "Name": "Station 19 - Mt. Tabor"                    },                    "geometry": {                        "x": 7667098.6735564321,                        "y": 683759.96555118263                    }                },                {                    "attributes": {                        "OBJECTID": 28,                        "Address": "13313 NE SAN RAFAEL ST",                        "Name": "Station 30 - Gateway"                    },                    "geometry": {                        "x": 7683049.5,                        "y": 688545.93766404688                    }                },                {                    "attributes": {                        "OBJECTID": 29,                        "Address": "5707 SE 92ND AVE",                        "Name": "Station 11 - Lents"                    },                    "geometry": {                        "x": 7671504,                        "y": 668305.31233595312                    }                },                {                    "attributes": {                        "OBJECTID": 30,                        "Address": "5 SE MADISON ST",                        "Name": "Station 21 - Eastbank/Hawthrone"                    },                    "geometry": {                        "x": 7646356.9816273004,                        "y": 680651.46916010976                    }                },                {                    "attributes": {                        "OBJECTID": 31,                        "Address": "1927 SE 174TH AVE",                        "Name": "Station 31 - Rockwood"                    },                    "geometry": {                        "x": 7693238.4950787425,                        "y": 677792.48064304888                    }                }            ]        }        x_coor = parameters[2].value        y_coor = parameters[3].value                incidents = {            "displayFieldName": "",            "fieldAliases": {                "OBJECTID": "OBJECTID",                "Name": "Name"            },            "geometryType": "esriGeometryPoint",            "spatialReference": {                "wkid": 2913,                "latestWkid": 2913            },            "fields": [                {                    "name": "OBJECTID",                    "type": "esriFieldTypeOID",                    "alias": "OBJECTID"                },                {                    "name": "Name",                    "type": "esriFieldTypeString",                    "alias": "Name",                    "length": 500                }            ],            "features": [                {                    "attributes": {                        "OBJECTID": 1,                        "Name": "1020 SE 7th Ave, Portland, Oregon, 97214"                    },                    "geometry": {                        "x": x_coor,                        "y": y_coor                    }                }            ]        }        # Connect to the closest facility service        api_key = "AAPK48cecd16fc9346a98e03f65a2cc0fce11Bx8ccleUqMD3VV-P8brDfuj98-nVfe1bj2qY9WrBeKIoohD2Fy3F2aCjaG1STj4"        arcgis.GIS("https://www.arcgis.com", api_key=api_key)        # Call the closest facility service        result = arcgis.network.analysis.find_closest_facilities(facilities=facilities,                                                                incidents=incidents,                                                                number_of_facilities_to_find=2,                                                                cutoff=5,                                                                travel_direction="Facility to Incident",                                                                time_of_day=datetime.datetime.utcnow(),                                                                time_of_day_usage="Start Time",                                                                populate_directions=True                                                                )        pd.set_option("display.max_rows", None)        pd.set_option("display.max_colwidth", None)        output_routes = result.output_routes.sdf        print("\n-- Output Routes -- \n")        messages.addMessage(output_routes[["Name", "Total_Minutes", "Total_Miles", "Total_Kilometers"]].to_string(index=False))        out_directions = result.output_directions.sdf[["RouteName", "Text"]]        print("\n-- Output Directions -- \n")        for route_name in out_directions["RouteName"].unique():            messages.addMessage(f"\n| {route_name} |\n")            messages.addMessage(out_directions["Text"].to_string(index=False))        #print_result(result)        #json_output = json.loads(result.output_routes)        output_feature_set = result.output_routes        features = output_feature_set.features        messages.addMessage(output_feature_set.to_json)        feature_list = json.loads(output_feature_set.to_json)        toolbox_dir = os.path.dirname(__file__)        # Construct the path of the output file relative to the Python Toolbox file        output_file = os.path.join(toolbox_dir, "output.json")        # Write the GeoJSON to a file        with open(output_file, "w") as f:            f.write(json.dumps(feature_list))        messages.addMessage("Output written to {}".format(output_file))        input_json = r"C:\Users\chans\my_project\GADEP\Projects\GADEP\output.json"        output_fc = r"C:\Users\chans\my_project\GADEP\Projects\GADEP\GADEP.gdb\output_fc"        arcpy.conversion.JSONToFeatures(input_json, output_fc)        aprx = arcpy.mp.ArcGISProject("CURRENT")  # Get the current project        map = aprx.activeMap  # Get the current map        layer = map.addDataFromPath(output_fc)  # Add the feature class to the map as a layer    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        return        # --------------------------------------------------------------------    # Checks a string if it contains blanks. If it does, get rid of them.    # --------------------------------------------------------------------def name_checker(name):    # If it contains a blank, change the case of the sring to title case (it looks better), and get rid of the blanks    return name.title().replace(" ", "") if " " in name else name# --------------------------------------------------------------------# Checks if a value is an empty string or not.# If it is, return a default value, else return the original value# --------------------------------------------------------------------def analysis_name(parameter, defaultName):     return defaultName if parameter == "" or parameter == " " or parameter == "#" else name_checker(parameter)def random_rgb():    r = random.randint(0,255)    g = random.randint(0,255)    b = random.randint(0,255)    # Return RGB array with an alpha value of 100.    # The alpha value dictates the color transparency - we don't wan't any transparency.    return [r, g, b, 100]# --------------------------------------------------------------------# This function converts a non-point feature layer to a point feature layer.# The first paramter is the non-point feature layer, and the second parameter is the# directory where the point feature layer will be written to.# --------------------------------------------------------------------def feature_to_point(inFeature, outFeature):    # Get descriptive properties of the feature layer to be converted    inFeatureDesc = arcpy.Describe(inFeature)    # If the feature layer is already a point feature, then return the point feature    if inFeatureDesc.shapeType == "Point":        return inFeature    else:        # Status message        message("Your input is not a point feature, it will be converted to one in order to continue with the analysis.")        # Perform the conversion        arcpy.FeatureToPoint_management(inFeature, outFeature, "INSIDE")        # Return the directory where the point feature is located        return outFeaturedef message(message):    arcpy.AddMessage(message)# Connect to the closest facility service and call itdef field_as_dict(field):    field_dict = {"name": field.name, "type": field.type, "alias": field.aliasName}    if field.type == "String":        field_dict["length"] = field.length    return field_dict'''def print_result(result):    """Print useful information from the result."""    pd.set_option("display.max_rows", None)    pd.set_option("display.max_colwidth", None)    output_routes = result.output_routes.sdf    print("\n-- Output Routes -- \n")    messages.addMessage(output_routes[["Name", "Total_Minutes", "Total_Miles", "Total_Kilometers"]].to_string(index=False))    out_directions = result.output_directions.sdf[["RouteName", "Text"]]    print("\n-- Output Directions -- \n")    for route_name in out_directions["RouteName"].unique():        messages.addMessage(f"\n| {route_name} |\n")        messages.addMessage(out_directions["Text"].to_string(index=False))'''