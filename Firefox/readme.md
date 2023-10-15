# firefox
This project runs a firefox browser on Cradlepoint Routers (with configurable start page).

## Setup:
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("firefox") and click on the Compose tab.
- Paste the following YAML into the compose tab of your project and click save:
> Set the environment variable FF_OPEN_URL to your start page of choice.

```yaml
version: '3'
services:
  firefox:
    image: jlesage/firefox
    restart: unless-stopped
    environment:
     - FF_OPEN_URL=https://google.com
    ports:
     - 5800:5800
    volumes:
     - 'config:/config'
     - 'etc:/etc'
volumes:
  config:
    driver: local
  etc:
    driver: local
```


## Usage:  
- Create an NCM Remote Connect LAN Manager profile for "Firefox" on 127.0.0.1 port 5800 HTTP
- Connect to the Firefox profile

## Docker Hub:  
https://hub.docker.com/r/jlesage/firefox
