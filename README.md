# GIS-based-Analysis-Tool-for-Disaster-Recovery

The project, GIS-based Analysis Tool for Disaster Recovery, references a tool-set of software interfaces which have been developed by us to help Emergency Managers in planning recovery efforts and forming evacuation plans in the event of and in preparation for a natural disaster.  The tool-set includes multiple ArcGIS Pro Toolboxes for GIS experts to extend their tool-chains in their analysis of natural disasters, as well as a stand-alone web-map for all to use in calculating routes that avoid geographic hazards.

## Repository Content
- arcGIS Toolboxes are located in `gis/toolboxes`:
  - [HazardRouting.pyt](https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/wiki/Hazard-Route-Toolbox) is a toolbox for performing hazard-avoiding route computation
  - [ClosestFacilties.pyt](https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/wiki/Route-Analysis-Toolbox) is a toolbox that acts as a API wrapper for ESRI's Closest Facilities API
  - Isochrones.pyt is an unfinished toolbox that acts as an API wrapper for the Ischrones service for the Open Routing Service 
- Web-map code is located in the root directory:
  - The `app.py` acts as the entry point for Flask, with `directionAPI.py` containing functions to access all the other APIs we used (Open Routing Service + ESRI Closest Facilities)
  - Our frontend is located under `templates` as `main.html` (the static directory contains some css and js dependencies like leaflet).

## Loading the ArcGIS Toolboxes:
Copied from our [wiki](https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/wiki/Hazard-Route-Toolbox):

After opening a project, navigate to the View pane and click the catalog button.
<kbd><img src="https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/blob/leechans/images/1.JPG" width="500"></kbd>

Then, navigate to the RouteAPI Python Toolbox to access the Closest Facilities Toolbox script.

<kbd><img src="https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/blob/leechans/images/2.JPG" width="500"></kbd>

This will then add the toolbox to your ArcGIS Pro project and can be accessible under the "catalog" widget.

## Locally testing the Web-Map
To run the web-map locally:

1. Install dependencies
```
pip install -r requirements.txt
```

2. Run flask
```
flask run
```

And that should run the service! (Note: you may also want to change the API endpoints used in `directionsAPI.py` as they currently reference our deployed instance of the open-routing-service which is liable to go offline in the future.)

## Deploying the Web-Map
Copied from our [wiki](https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery/wiki/Guide:-Deploying-Services):


This guide documents how we deployed an instance of the Open-Routing Service (which we used for routing computation) as well as how we deployed the web-map.  Below you can see a crude ascii diagram of our basic tech-stack (ascii diagram generated with the help of [ASCIIflow](https://asciiflow.com/#/))

Basically, our web-services comprised of two docker containers behind an nginx proxy which we ran on a Digital Ocean droplet (Linux cloud VM).  

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│     ┌─────────────────────────┐                   Digital Ocean Droplet      │
│     │                         │                                              │
│     │ nginx docker container  │                                              │
│     │  ┌─────────────────┐    │                                              │
│     │  │ web-map (flask) │    │                                              │
│     │  └─────────────────┘    │                                              │
│     │                         │                                              │
│     └─────────────────────┬───┘                                              │
│                           │                        ┌────────────┐            │
│                           └────────────────────────►            │            │
│                                                    │   nginx    │            │
│                           ┌────────────────────────►            │            │
│                           │                        └────────────┘            │
│                           │                                                  │
│     ┌─────────────────────┴───┐                                              │
│     │                         │                                              │
│     │                         │                                              │
│     │   Open Routing Service  │                                              │
│     │                         │                                              │
│     │                         │                                              │
│     └─────────────────────────┘                                              │
│                                                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Infrastructure (VM Config)
For our use-case, we deployed our software on a Digital Ocean Droplet with about 2GB of memory and otherwise minimum specifications (approximately $12 per month).  However, any server which you can setup nginx & docker should work for deployment purposes.

For setting up the open-routing service, the amount of allotted memory matters a significant bit for how much data you want the service to handle (since all the computed graph data mostly resides in memory).  The Open Routing Service has some good explanations [here](https://giscience.github.io/openrouteservice/installation/System-Requirements) about the proper system requirements, but for our use-case, we could configure the software to run with the data extract of Oregon (205 MB) with about 1.7 GB of memory in use by the service.


### UFW
We used ufw (the default ubuntu firewall utility) to open/close ports for our VM so we could minimize the open ports on our machine.  We enabled only ports 22 (for ssh) 8080 (where we served the open-routing-service) and 443 (for https).  The article linked [here](https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands) explains the intricacies of using the utility.

## Open Routing Service
For setting up the [Open Routing Service](https://github.com/GIScience/openrouteservice), we relied on the already existing documentation on how to setup the [service](https://giscience.github.io/openrouteservice/installation/Installation-and-Usage.html) using Docker.

For our data-extract, we just used the state of Oregon extract provided by Geofabick [here](https://download.geofabrik.de/north-america/us.html).


## Web-Map
For our web-map, we used a pre-configured [nginx-uWSGI docker image](https://github.com/tiangolo/uwsgi-nginx-flask-docker) to easily get the web-map running on our cloud VM.  The basic deployment process we used went as follows:

1. `git clone https://github.com/Jaron-U/GIS-based-Analysis-Tool-for-Disaster-Recovery` and then `git pull` (for any subsequent changes we pushed to the code-base)

2. built the image `docker build . -t webmap`

3. Then created the docker container with `docker run -d -p 127.0.0.1:9955:80 webmap`

## Nginx Proxy Setup
After we had the web-map running, we configured nginx as a reverse-proxy to forward the open-routing-service and our web-map to ports 443 and 8080.

We registered a domain name (safer-ways.com for about $12/year) and then configured a DNS record for `map.safer-ways.com` to map to our cloud VM's IP address.

To enable HTTPS (which we needed for the Browser Geolocation API to work) we used [certbot](https://certbot.eff.org/) to automatically configure it.

