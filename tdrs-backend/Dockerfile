FROM python:3.10.8-slim-buster
ENV PYTHONUNBUFFERED 1

ARG user=tdpuser
ARG group=tdpuser
ARG uid=1000
ARG gid=1000
ENV DJANGO_SETTINGS_MODULE=tdpservice.settings.local
ENV DJANGO_CONFIGURATION=Local
# Allows docker to cache installed dependencies between builds
COPY Pipfile Pipfile.lock /tdpapp/
WORKDIR /tdpapp/
# Download latest listing of available packages:
RUN apt-get -y update
# Upgrade already installed packages:
RUN apt-get -y upgrade
# Install a new package:
RUN apt-get install -y gcc && apt-get install -y graphviz && apt-get install -y graphviz-dev
RUN apt-get install postgresql-client -y
# Install pipenv
RUN pip install --upgrade pip pipenv
RUN pipenv install --dev --system --deploy

# Adds our application code to the image
COPY . /tdpapp
WORKDIR /tdpapp/

RUN groupadd -g ${gid} ${group} && useradd -u ${uid} -g ${group} -s /bin/sh ${user}

RUN chown -R tdpuser /tdpapp && chmod u+x gunicorn_start.sh wait_for_services.sh

#CMD ["./gunicorn_start.sh"]
# if the container crashes/loops, we can shell into it by doing the following:
# docker ps -a # to get the container id
# docker commit <container id> debug/<new image name>
# docker run -it --rm --entrypoint /bin/bash debug/<new image name>
