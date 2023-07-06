# pihole
This project runs a pihole server for content filtering and DHCP.

## Setup:
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("pihole") and click on the Compose tab.
- Paste the following YAML into the compose tab of your project and click save:

```yaml
version: '2.4'
services:
  pihole:
    image: pihole/pihole
    restart: unless-stopped
    environment:
      - TZ=America/Denver
      - WEBPASSWORD=password
      - PIHOLE_UID=0
    cap_add:
     - NET_ADMIN
    networks:
      lannet:
        ipv4_address: 192.168.0.2
    volumes:
      - 'etc:/etc'
volumes:
  etc:
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
- Browse to the IP address of the pihole container with /admin on the URL (e.g. http://192.168.0.2/admin)

## Docker Hub:  
https://hub.docker.com/r/pihole/pihole