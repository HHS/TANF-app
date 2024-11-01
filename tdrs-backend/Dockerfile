FROM python:3.10.8-slim-bullseye
ENV PYTHONUNBUFFERED 1

ARG user=tdpuser
ARG group=tdpuser
ARG uid=1000
ARG gid=1000
ENV DJANGO_SETTINGS_MODULE=tdpservice.settings.local
ENV DJANGO_CONFIGURATION=Local
# Allows docker to cache installed dependencies between builds
COPY Pipfile Pipfile.lock /tdpapp/
COPY sources.list /etc/apt/sources.list
WORKDIR /tdpapp/
# Download latest listing of available packages:
RUN apt-get -y update
# Upgrade already installed packages:
RUN apt-get -y upgrade
# Install packages:
RUN apt-get install -y gcc graphviz graphviz-dev libpq-dev python3-dev vim curl ca-certificates

# Postgres client setup
#RUN bash -c 'echo "deb [trusted=yes] https://tdp-nexus.dev.raftlabs.tech/repository/apt-proxy-postgres/ bullseye-pdpg main" >> /etc/apt/sources.list'
RUN apt-get update -y && apt-get upgrade -y
RUN apt install -y postgresql-common && install -d /usr/share/postgresql-common/pgdg && \
sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc trusted=yes] https://tdp-nexus.dev.raftlabs.tech/repository/apt-proxy-postgres/ bullseye-pgdg main" >> /etc/apt/sources.list' && \
curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
apt -y update && apt -y upgrade && apt install postgresql-client-15 -y

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
