#!/bin/bash
set -e

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
TAG="${BUILD_DATE}_build-${BUILD_NUM}_${COMMIT_HASH}"

BUILD_DATE=`date +%F`

pwd
ls
ls $BACKEND_PATH
ls $FRONTEND_PATH

build_and_tag() {
    echo "$DOCKER_LOGIN" | docker login https://tdp-docker.dev.raftlabs.tech -u $DOCKER_USER --password-stdin
    for platform in "linux/amd64" "linux/arm64"; do
        docker build --platform $platform -t tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME:$TAG -t tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
        docker build --platform $platform -t tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME:$TAG -t tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"

        docker push tdp-docker.dev.raftlabs.tech/$BACKEND_APP_NAME --all-tags
        docker push tdp-docker.dev.raftlabs.tech/$FRONTEND_APP_NAME --all-tags
    done
    docker logout
}

echo "Building and Tagging images for $BACKEND_APP_NAME and $FRONTEND_APP_NAME"
build_and_tag
