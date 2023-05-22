# GIS-based-Analysis-Tool-for-Disaster-Recovery

The project, GIS-based Analysis Tool for Disaster Recovery, references a tool-set of software interfaces which have been developed by us to help Emergency Managers in planning recovery efforts and forming evacuation plans in the event of and in preparation for a natural disaster.  The tool-set includes multiple ArcGIS Pro Toolboxes for GIS experts to extend their tool-chains in their analysis of natural disasters, as well as a stand-alone web-map for all to use in calculating routes that avoid geographic hazards.

## Repository Layout
- arcGIS Toolboxes are located in `gis/toolboxes`
- Web-map code is located in the root directory.

## Main points about the project to remember when developing
This project is a combination of two different parts when boiled down; its arcGIS toolboxes, and its Web-map. <br />
The Web-map backend runs on Flask, which you can run tests on locally but will need to deploy through external services to make public: The documentation for Flask can be found here: [Flask reference](https://flask.palletsprojects.com/en/2.3.x/) <br />
To display the map element on the frontend of the Web-map, Leaflet is used. Their documentation can be found here: [Leaflet reference](https://leafletjs.com/reference.html) <br />
-MORE TO ADD? APPEND- <br />
<br />
If you need to or want to know more specific details, you should flip over to the [wiki](https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/wiki) since it is a good place to check for project information
