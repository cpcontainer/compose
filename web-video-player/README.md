# web-video-player
This project runs the cpcontainer/web-video-player image which runs an NGINX webserver with javascript video player.  
This is useful for demonstrating container capabilities and testing connectivity across network segments.

![image](https://user-images.githubusercontent.com/127797701/227572301-9e188cd4-3794-4157-bfa2-2d68dfa26131.png)

## Setup:  
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("web-video-player") and click on the Compose tab.  
- Paste the following YAML into the compose tab of your project and click save:  
  
```yaml
version: '2.4'
services:
  video:
    image: 'cpcontainer/web-video-player'
    restart: unless-stopped
    ports:
     - 8000:80
```
  
## Usage:  

#### NCM:  
- Use NCM Remote Connect LAN Manager to create a profile for "web-video-player" at 127.0.0.1 port 8000 protocol HTTP.   
- Connect to the "web-video-player" profile you created.  
  
#### Local:
- In the routers Zone Firewall, forward the PrimaryLAN Zone to the Router with DefaultAllowAll policy.
- Browse to the IP address of your router, port 8080 (e.g. http://192.168.0.1:8000)

## Docker Hub:  
https://hub.docker.com/r/cpcontainer/web-video-player
