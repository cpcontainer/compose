# OpenSpeedtest
This project runs the openspeedtest/latest container which runs a web based speedtest server.



## Setup:
- Edit your Cradlepoint router configuration and navigate to System > Containers > Projects and click Add.  
- Give your project a name ("OpenSpeedtest") and click on the Compose tab.
- Paste the following YAML into the compose tab of your project and click save:

```yaml
version: '2.4'
services:
    speedtest:
        image: openspeedtest/latest
        restart: unless-stopped
        ports:
            - '3000:3000'
```


## Usage:  
Browse to your routers IP address on port 3000.
e.g. http://192.168.0.1:3000

Stress Test. (Continuous Speed Test)

To enable the stress test. Pass Stress or S keyword as a URL parameter.


http://192.168.1.5?Stress=Low

After the STRESS or S keyword, you can specify the number of seconds you need to run the StressTest in seconds, or preset values such as Low, Medium, High, VeryHigh, Extreme, Day, and Year. Will run a speed test for 300,600,900,1800,3600,86400,31557600 seconds, respectively. Also, you can feed the first letter of each parameter and its values.


http://192.168.1.5?S=L

S=L is the same as passing Stress=low

Or you can specify the number of seconds eg:5000 directly without any preset keywords.


http://192.168.1.5?Stress=5000

Run a speed test automatically

Run a speed test automatically on page load.


http://192.168.1.5?Run

Run a speed test automatically after a few seconds.


http://192.168.1.5?Run=10 or http://192.168.1.5?R=10

You can pass multiple keywords, and it's not Case-Sensitive.


http://192.168.1.5?Run&Stress=300 OR http://192.168.1.5?R&S=300

This will start a speed test immediately and run for 300 seconds in each direction. That is 300 seconds for download and 300 seconds for upload.