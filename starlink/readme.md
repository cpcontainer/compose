# Starlink
This project runs a modified version of https://github.com/sparky8512/starlink-grpc-tools to get status from a Starlink device and populate /status/starlink/.  It also puts brief status in the asset_id field for viewing in the NCM devices grid.  A web UI runs on port 8000 with live status and buttons to Reboot, Stow, and Unstow the Starlink device.  

## Setup:
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("Starlink") and click on the Compose tab.
- Paste the following YAML into the compose tab of your project and click save:

```yaml
version: '3'
services:
  starlink:
    image: cpcontainer/starlink
    container_name: starlink
    restart: unless-stopped
    ports:
    - 8000:8000
    volumes:
    - ${CONFIG_STORE}
```


## Usage:  
- Create an NCM Remote Connect LAN Manager profile for "Starlink" on 127.0.0.1 port 8000 HTTP
- Connect to the Starlink profile

## Docker Hub:  
https://hub.docker.com/r/cpcontainer/starlink