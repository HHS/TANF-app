FROM python:3.8
ENV PYTHONUNBUFFERED 1

ARG user=tdpuser
ARG group=tdpuser
ARG uid=1000
ARG gid=1000

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . /tdpapp
WORKDIR /tdpapp/

RUN groupadd -g ${gid} ${group} && useradd -u ${uid} -g ${group} -s /bin/sh ${user}

RUN chown -R tdpuser /tdpapp


EXPOSE 8000

# Run the production server
CMD newrelic-admin run-program gunicorn --bind 0.0.0.0:$PORT --access-logfile - tdpservice.wsgi:application
