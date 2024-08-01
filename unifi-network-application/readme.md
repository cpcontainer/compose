# unifi-network-application
This project runs the Unifi Network Application WiFi Controller (ui.com)

![image](https://github.com/user-attachments/assets/19007fe2-2552-4ca0-a16a-f1e199fd78fb)

## Setup:
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("Unifi") and click on the Compose tab.
- Paste the following YAML into the compose tab of your project and click save:

```yaml
version: "2.1"
services:
  unifi-network-application:
    image: lscr.io/linuxserver/unifi-network-application:latest
    container_name: unifi
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - MONGO_USER=unifi
      - MONGO_PASS=unifi
      - MONGO_HOST=unifi-db
      - MONGO_PORT=27017
      - MONGO_DBNAME=unifi
    volumes:
      - etc:/etc
      - usr:/usr
    restart: unless-stopped
    networks:
      lannet:
        ipv4_address: 192.168.0.2
  unifi-db:
    image: phate999/unifi-db
    container_name: unifi-db
    volumes:
      - db:/data/db
    restart: unless-stopped
    networks:
      lannet:
        ipv4_address: 192.168.0.3
volumes:
  etc:
    driver: local
  usr:
    driver: local
  db:
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
- Create an NCM Remote Connect LAN Manager profile for "Unifi" on 192.168.0.2 port 8443 HTTPS
- Connect to the "Unifi" profile

## Docker Hub:  
https://hub.docker.com/r/linuxserver/unifi-network-application
