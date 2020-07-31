FROM python:3.8
ENV PYTHONUNBUFFERED 1

ARG user=tdpuser
ARG group=tdpuser
ARG uid=1000
ARG gid=1000
ENV DJANGO_SECRET_KEY=rp3l\&amp\;dm517lw\$7m78q\&amp\;sp6y2way\^gix%0sto%\^709jp25\*x\!d6
ENV DJANGO_SETTINGS_MODULE=tdpservice.settings.local
ENV DJANGO_CONFIGURATION=Local

#ENV DJANGO_SETTINGS_MODULE=tdpservice.settings.production
#ENV DJANGO_CONFIGURATION=Production
# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . /tdpapp
WORKDIR /tdpapp/

RUN groupadd -g ${gid} ${group} && useradd -u ${uid} -g ${group} -s /bin/sh ${user}

RUN chown -R tdpuser /tdpapp
RUN chmod u+x  gunicorn_start.sh

EXPOSE 8090


CMD ["./gunicorn_start.sh"]

# Run the production server
#CMD newrelic-admin run-program gunicorn --bind 0.0.0.0:8000 --access-logfile - tdpservice.wsgi:application
 