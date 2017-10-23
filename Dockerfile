FROM ubuntu:16.04

# Install python, redis, supervisor, nginx
RUN apt-get update && apt-get install -y python3 python3-dev python3-venv python3-setuptools python3-pip redis-server libssl-dev libbz2-dev libffi-dev supervisor nginx

# Install gunicorn
RUN pip3 install gunicorn

# Clear default nginx site and replace it with our own
RUN rm /etc/nginx/sites-available/default
RUN /bin/bash -c "echo $'server { \n\
    listen 80; \n\
    location /static/ { \n\
        alias /var/www/Auth/static/; \n\
        autoindex off; \n\
    } \n\
    location / { \n\
        include proxy_params; \n\
        proxy_pass http://127.0.0.1:8000; \n\
    } \n\
}' >> /etc/nginx/sites-available/default"

# Create allianceserver
RUN adduser --disabled-login allianceserver

# Install auth
WORKDIR /home/allianceserver/
COPY ./ allianceauth/
RUN pip3 install -e ./allianceauth

# Create auth project
RUN allianceauth start Auth
RUN echo "DEBUG = True" >> Auth/Auth/settings/local.py
RUN python3 Auth/manage.py migrate

# Collect static
RUN mkdir -p /var/www/Auth/static
RUN python3 Auth/manage.py collectstatic

# Set user permissions
RUN chown -R www-data:www-data /var/www/Auth
RUN chown -R allianceserver:allianceserver Auth

# Link supervisor config
RUN ln Auth/supervisor.conf /etc/supervisor/conf.d/Auth.conf

# Open port 80 to serve site
EXPOSE 80

# Start webserver and celery on container start
ENTRYPOINT service supervisor start && service nginx start && service redis-server start && /bin/bash

# Set default directory
WORKDIR /home/allianceserver/Auth

# Set python aliases
RUN echo "alias python=python3" >> ~/.bashrc
RUN echo "alias pip=pip3" >> ~/.bashrc
