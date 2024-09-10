#!/bin/bash

if [ "$#" -ne 8  ]; then
    echo "Error, this script expects 8 parameters."
    echo "I.e: ./build-tag-images.sh BACKEND_APP_NAME FRONTEND_APP_NAME BACKEND_PATH FRONTEND_PATH BUILD_NUM COMMIT_HASH DOCKER_LOGIN DOCKER_USER"
    exit 1
fi

BACKEND_APP_NAME=$1
FRONTEND_APP_NAME=$2
BACKEND_PATH=$3
FRONTEND_PATH=$4
BUILD_NUM=$5
COMMIT_HASH=$6
DOCKER_LOGIN=$7
DOCKER_USER=$8
BUILD_DATE=`date +%F`
TAG="${BUILD_DATE}_build-${BUILD_NUM}_${COMMIT_HASH}"

export DOCKER_CLI_EXPERIMENTAL=enabled

build_and_tag() {
    echo "$DOCKER_LOGIN" | docker login https://tdp-docker.dev.raftlabs.tech -u $DOCKER_USER --password-stdin
    docker buildx build --load --platform linux/amd64 -t tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME:$TAG -t tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
    docker buildx build --load --platform linux/arm64 -t tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME:$TAG -t tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
    docker push --all-tags tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME
    docker buildx build --load --platform linux/amd64 -t tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME:$TAG -t tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"
    docker buildx build --load --platform linux/arm64 -t tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME:$TAG -t tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"
    docker push --all-tags tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME
    docker logout
}

echo "Building and Tagging images for $BACKEND_APP_NAME and $FRONTEND_APP_NAME"
build_and_tag
