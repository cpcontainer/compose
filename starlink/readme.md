# Starlink
This project runs a modified version of https://github.com/sparky8512/starlink-grpc-tools to get status from a Starlink device and populate /status/starlink/.  It also puts brief status in the asset_id field for viewing in the NCM devices grid.  A web UI runs on port 8000 with live status and buttons to Reboot, Stow, and Unstow the Starlink device.  

![image](https://github.com/user-attachments/assets/ba815be4-af4f-4d50-812f-29a0927e3a4e)

![image](https://github.com/user-attachments/assets/6b832f09-9659-43fe-b694-0ded30812b02)

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
