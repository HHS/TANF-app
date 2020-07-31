FROM python:3.8
ENV PYTHONUNBUFFERED 1

ARG user=tdpuser
ARG group=tdpuser
ARG uid=1000
ARG gid=1000
ENV DJANGO_SECRET_KEY=w0&df2562wx3g9(cddtwtq)s*3k5jyza8*xwka$+=ya21h@#b(
ENV DJANGO_SETTINGS_MODULE=tdpservice.settings.production
ENV DJANGO_CONFIGURATION=Production

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Adds our application code to the image
COPY . /tdpapp
WORKDIR /tdpapp/

RUN groupadd -g ${gid} ${group} && useradd -u ${uid} -g ${group} -s /bin/sh ${user}

RUN chown -R tdpuser /tdpapp
RUN chmod u+x  gunicorn_start.sh

EXPOSE 8000


CMD ["./gunicorn_start.sh"]
