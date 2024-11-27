#!/bin/sh

printenv >> /etc/environment
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
cd /app
python $@ &
python webserver.py
