FROM php:7.4-apache

# install grpcurl
WORKDIR /usr/local/bin
RUN cd /usr/local/bin && curl -L https://github.com/fullstorydev/grpcurl/releases/download/v1.9.2/grpcurl_1.9.2_linux_arm64.tar.gz -o grpcurl.tar.gz && tar -xzvf grpcurl.tar.gz && rm grpcurl.tar.gz

# install git, speedtest
RUN apt-get update -y && apt-get install -y speedtest-cli cron

# clone repo
WORKDIR /var/www/html
COPY . /var/www/html

# Snag favicon from Starlink
RUN curl https://www.starlink.com/assets/favicon.ico > favicon.ico

# schedule speedtest
RUN echo "*/15 * * * * /usr/local/bin/php /var/www/html/scripts/cron/php/speedtest.cron.php" >> /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root
RUN chown root.crontab /var/spool/cron/crontabs/root

# Set ServerName to suppress the warning
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# start apache and run update scripts
CMD ["/bin/bash", "-c", "/etc/init.d/apache2 start && cron && /var/www/html/scripts/binbash/starlink.history.update.sh & /var/www/html/scripts/binbash/starlink.update.sh"]
