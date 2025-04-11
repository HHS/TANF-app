FROM elipe17/tdp-backend-base:v0.0.2

# Adds our application code to the image
COPY . /tdpapp
WORKDIR /tdpapp/

RUN chown -R tdpuser /tdpapp && chmod u+x gunicorn_start.sh wait_for_services.sh

#CMD ["./gunicorn_start.sh"]
# if the container crashes/loops, we can shell into it by doing the following:
# docker ps -a # to get the container id
# docker commit <container id> debug/<new image name>
# docker run -it --rm --entrypoint /bin/bash debug/<new image name>

# Links this container to the rpo in GHCR
LABEL org.opencontainers.image.source=https://github.com/raft-tech/TANF-app
LABEL org.opencontainers.image.description="Backend API Service for TDP."
LABEL org.opencontainers.image.licenses=CC0-1.0
