# Traccar
This project runs a Traccar AVL Server in a container.

## Setup:
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("Traccar") and click on the Compose tab.
- Paste the following YAML into the compose tab of your project and click save:
> Edit the network configuration as necessary for your router.

```yaml
version: '3'
services:
  traccar:
    image: traccar/traccar:ubuntu
    networks:
      lannet:
        ipv4_address: 192.168.0.2
    volumes:
     - traccar:/opt/traccar
volumes:  
  traccar:  
    driver: local
networks:
  lannet:
    driver: bridge
    driver_opts:
      com.cradlepoint.network.bridge.uuid: 00000000-0d93-319d-8220-4a1fb0372b51
    ipam:
      driver: default
      config:
        - subnet: 192.168.0.0/24
          gateway: 192.168.0.1

```


## Usage:  
- Create an NCM Remote Connect LAN Manager profile for "Traccar" on port 8082 HTTP for the IP Address of your container (e.g. 192.168.0.2)
- Connect to the Traccar profile
- Default user/pass is admin/admin

## Docker Hub:  
https://hub.docker.com/r/traccar/traccar