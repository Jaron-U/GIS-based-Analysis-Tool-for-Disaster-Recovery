# -*- coding: utf-8 -*-

import arcpy
import random
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Disaster Route P"
        self.alias = "Disaster Route P"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Disaster Route P"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
         # First parameter
        param0 = arcpy.Parameter(
            displayName="Run Disaster Impact Tool",
            name="Run_Disaster_Impact_Tool",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Earthquake Magnitude",
            name="Earthquake_Magnitude",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Starting Points (Incidents)",
            name="Starting_Points_(Incidents)",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Incidnts Filter",
            name="Incidnts_Filter",
            datatype="GPSQLExpression",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param4 = arcpy.Parameter(
            displayName="End Points (Facilities)",
            name="End_Points_(Facilities)",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param5 = arcpy.Parameter(
            displayName="Facilities Filter",
            name="Facilities_Filter",
            datatype="GPSQLExpression",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param6 = arcpy.Parameter(
            displayName="Number of Facilities",
            name="Number_of_Facilities",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param7 = arcpy.Parameter(
            displayName="Analsis Name",
            name="Analsis_Name",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        # # Second parameter
        # param8 = arcpy.Parameter(
        #     displayName="Overwrite Existing Analysis",
        #     name="Overwrite_Existing_Analysis",
        #     datatype="GPString",
        #     parameterType="Optional",
        #     direction="Input")

        param3.parameterDependencies = [param2.name]
        param5.parameterDependencies = [param4.name]
        
        # params = [param0, param1, param2, param3, param4, param5, param6, param7, param8]
        params = [param0, param1, param2, param3, param4, param5, param6, param7]
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
        scriptsPath = os.getcwd()
        # params = getParameterInfo()

        # However, we want to get the parent directory of the script. We'll get something like this:
        # {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP
        # Then, in the same line, we compose a new directory.
        # The resulting directory will look something like this:
        # {YOUR LOCAL DRIVE}\{OTHER FOLDERS}\GADEP\Projects\GADEP
        projectPath = os.path.join(os.path.dirname(scriptsPath), "Projects", "GADEP")

        # Now that we have the main project path stored as a variable, we can use it to 
        # compose a path for other directories we need to traverse to
        # Path to "Infrastructures.gdb"
        infrastructuresPath = os.path.join(projectPath, "Infrastructures.gdb")

        # Path to "NetworkAnaysis.gdb"
        networkAnalysisPath = os.path.join(projectPath, "NetworkAnalysis.gdb")

        # Path to "TransportationNetwork.gdb"
        transportationNetworkPath = os.path.join(projectPath, "TransportationNetwork.gdb")

        # Path to the "GADEP.gdb"
        gadepPath = os.path.join(projectPath, "GADEP.gdb")

        # ////////////////////////////////////////////////////////////////////
        # Disaster impact - bridges
        # ////////////////////////////////////////////////////////////////////

        # Get the boolean value of the first parameter.
        runDisasterImpact = parameters[0].valueAsText

        # Filtered bridges layer to be used in the Select_analysis function
        bridgesFiltered = os.path.join(gadepPath, "BridgesFiltered")   

        # If the boolean is true, then the Disaster Impact tool will be ran using only the bridges as
        # its parameter.
        if runDisasterImpact:
            # Status messsage
            messages.addMessage("Running Disaster Impact tool...")
            # Bridges directory
            bridges = os.path.join(infrastructuresPath, "Bridges")
            # The earthquake magnitude chosen
            em = parameters[1].valueAsText

            # The Disaster Impact toolbox directory
            gadepToolBox = os.path.join(projectPath, "GADEP.tbx")

            # Import the Disaster Impact toolbox
            arcpy.ImportToolbox(gadepToolBox, "tool")
            # Run the Disaster Impact tool.
            # Here we use the string "Bridges" because the Disaster Impact tool checks the 
            # names of the feature layers contained in the "Infrastructures.gdb", and not
            # the full path of them.
            arcpy.DisasterImpact_tool("Bridges", em)

            # Success message
            messages.addMessage("Disaster Impact simulation successful!")

            # --------------------------------------------------------------------
            # BridgesFiltered layer for routing
            # --------------------------------------------------------------------
            # After the simulation is complete, we'll create a new map layer called "BridgesFiltered".
            # Using an SQL expression, this layer will consist of specific bridges given the expression.
            # This layer will serve as the PointBarriers feature for the routing.

            # The SQL expression that dictates what features will be selected
            whereClause = 'Damage = \'Slight\' Or Damage = \'Moderate\' Or Damage = \'Extensive\' Or Damage = \'Complete\''     

            # In the case that the bridge layer does not exist in the "Infrastructures.gdb", it will throw an error.
            # Wrap the next function in a try-except statement to handle this case.
            try: 
                # The Select_analysis will take in the latest data in the "Bridges" feature layer and create/replace the values of the 
                # 'BridgesFiltered' feature layer leaving only the values resulting from the SQL expression
                arcpy.Select_analysis(bridges, bridgesFiltered, whereClause)
            except:
                messages.addMessage("A possible error occurred but it was caught. \n\
                    After this script completes the simulation, it filters the 'Bridges' layer. \n\
                    It's possible that this layer does not exist yet.")

        messages.addMessage("Preparing for route analysis111...")

        # ////////////////////////////////////////////////////////////////////
        # Routing Analysis
        # ////////////////////////////////////////////////////////////////////
        # --------------------------------------------------------------------
        # Initializing variables for routing
        # --------------------------------------------------------------------
        network = os.path.join(transportationNetworkPath, "OregonNetwork", "OregonNetworkDataset")  # Analysis network
        travelMode = "Vehicle"                                                                      # Currently the only mode of transportation
        # The name of the output layer.
        # We concatenate a string of random integers at the end in order to create a unique layer each time.
        defaultLayerName = "ClosestFacilities" + str(random.randint(100000,999999))  

        # The incidents, facilities, and barriers that will be used in the analysis
        incidents = parameters[2].valueAsText
        print(parameters[2].valueAsText)
        incidentsWhereClause = parameters[3].valueAsText     # The SQL expression that will filter the incidents feature layer
        facilities = parameters[4].valueAsText
        facilitiesWhereClause = parameters[5].valueAsText       # The SQL expression that will filter the incidents feature layer
        numberOfFacilities = parameters[6].valueAsText          # The number of facilities parameter value
        analysisName = parameters[7].valueAsText                # The analysis name 
        # existingAnalysisName = parameters[8].valueAsText        # The existing analysis name

        # Try to onvert the number of facilities parameter to an integer
        try:
            numberOfFacilities = int(numberOfFacilities)
        # If we can't, then it's not a valid value. Default the value to 1.
        except:
            numberOfFacilities = 1

        # Set the current workspace to the "NetworkAnalysis.gdb"
        arcpy.env.workspace = networkAnalysisPath
        # Store the names of the existing route analyses in a list
        existingAnalyses = arcpy.ListFeatureClasses()

        print(existingAnalyses)

        # If the existing analysis name parameter value exists in the list of existing analyses, then it will be overwritten.
        # Else, a new layer will be created.
        # if existingAnalysisName in existingAnalyses:
        #     layerName = existingAnalysisName
        #     outputLayerFile = os.path.join(networkAnalysisPath, layerName)
        #     arcpy.Delete_management(outputLayerFile)

        #     messages.addMessage("Exisiting route layer will be overwritten.")
        # else:
        layerName = analysis_name(analysisName, defaultLayerName)
        #     outputLayerFile = os.path.join(networkAnalysisPath, layerName)
        #     messages.addMessage("New route layer will be created.")

        # --------------------------------------------------------------------
        # Filter incidents and facilities
        # --------------------------------------------------------------------
        # Status message
        messages.addMessage("Applying your filters (if you selected any)...")

        # If the incidents feature layer is not a point feature, e.g., a polygon shape, it will be converted
        # into a point feature. Else, it will not change.
        incidents = feature_to_point(incidents, os.path.join(gadepPath, "IncidentsPoints"))

        # The path for a new feature layer called "IncidentsFiltered"
        incidentsFiltered = os.path.join(gadepPath,"IncidentsFiltered")

        # The Select_analysis will take in the latest data in the "incidents" feature layer and create (or replace, if it exists) the values of the 
        # 'IncidentsFiltered' feature layer per the SQL expression
        arcpy.Select_analysis(incidents, incidentsFiltered, incidentsWhereClause)

        # If the facilities feature layer is not a point feature, e.g., a polygon shape, it will be converted
        # into a point feature. Else, it will not change.
        facilities = feature_to_point(facilities, os.path.join(gadepPath, "FacilitiesPoints"))

        # The path for a new feature layer called "IncidentsFiltered"
        facilitiesFiltered = os.path.join(gadepPath,"FacilitiesFiltered")

        # The Select_analysis will take in the latest data in the "incidents" feature layer and create (or replace, if it exists) the values of the 
        # 'IncidentsFiltered' feature layer per the SQL expression
        arcpy.Select_analysis(facilities, facilitiesFiltered, facilitiesWhereClause)

        # --------------------------------------------------------------------
        # Start analysis
        # Reference: https://pro.arcgis.com/en/pro-app/latest/arcpy/network-analyst/closestfacility.htm
        # --------------------------------------------------------------------
        # Status message
        messages.addMessage("Preparing route analysis...")

        # Network name
        ndLayerName = "OregonNetworkDataset"

        # Create a network dataset layer and get the desired travel mode for analysis
        arcpy.nax.MakeNetworkDatasetLayer(network, ndLayerName)

        # Instantiate a ClosestFacility solver object
        closestFacility = arcpy.nax.ClosestFacility(network)
        # Set properties
        closestFacility.travelMode = travelMode     # The mode of travel
        # The number of facilities the analysis will find for each incident
        closestFacility.defaultTargetFacilityCount = 1 if numberOfFacilities == "" or numberOfFacilities == "#" else int(numberOfFacilities)
        # Load inputs
        closestFacility.load(arcpy.nax.ClosestFacilityInputDataType.Facilities, facilitiesFiltered)
        closestFacility.load(arcpy.nax.ClosestFacilityInputDataType.Incidents, incidentsFiltered)
        closestFacility.load(arcpy.nax.ClosestFacilityInputDataType.PointBarriers, bridgesFiltered)

        # Status message
        messages.addMessage("Running analysis... Finding the nearest facilities.".format(numberOfFacilities))

        # --------------------------------------------------------------------
        # Solve and export analysis
        # --------------------------------------------------------------------
        result = closestFacility.solve()

        # Export the analysis as a route layer
        result.export(arcpy.nax.ClosestFacilityOutputDataType.Routes, outputLayerFile)

        # Status message
        messages.addMessage("Route analysis successful! Exporting the route layer...")

        # Add the route layer to the map
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprxMap = aprx.listMaps("Map")[0] 
        aprxMap.addDataFromPath(outputLayerFile)

        # --------------------------------------------------------------------
        # Adjust route layer properties
        # References:
        # https://pro.arcgis.com/en/pro-app/latest/arcpy/mapping/uniquevaluerenderer-class.htm
        # --------------------------------------------------------------------
        # Once the layer is added to the map, adjust its physical properties.
        # Get the layer first.
        lyr = aprxMap.listLayers(layerName)[0]
        # Symbology object with adjustable properties
        sym = lyr.symbology

        # Update the symbology to render a unique color for every unique IncidentOID value
        sym.updateRenderer('UniqueValueRenderer')
        sym.renderer.fields = ['IncidentOID']

        # Loop through the groups in the current unique value render.
        for grp in sym.renderer.groups:
            # Loop through the values in the group items (the group items are the values in the chosen renderer fields)
            for itm in grp.items:
                # For each layer:
                # 1. Change the symbol style
                itm.symbol.applySymbolFromGallery("Marker Arrow Line 3 (Bold)")
                # 2. Set a random color to it
                itm.symbol.outlineColor = {'RGB': random_rgb()}   

        # Apply new properties
        lyr.symbology = sym

        # Print success message
        messages.addMessage("Script completed successfully!")
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


