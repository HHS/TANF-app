#!/bin/bash

if [ "$#" -ne 9  ]; then
    echo "Error, this script expects 9 parameters."
    echo "I.e: ./build-tag-images.sh BACKEND_APP_NAME FRONTEND_APP_NAME BACKEND_PATH FRONTEND_PATH BUILD_NUM COMMIT_HASH REGISTRY_LOGIN REGISTRY_USER REGISTRY_DOMAIN"
    exit 1
fi

BACKEND_APP_NAME=$1
FRONTEND_APP_NAME=$2
BACKEND_PATH=$3
FRONTEND_PATH=$4
BUILD_NUM=$5
COMMIT_HASH=$6
REGISTRY_LOGIN=$7
REGISTRY_USER=$8
REGISTRY_DOMAIN=$9

STRIPPED_REGISTRY="${REGISTRY_DOMAIN#*://}" # removes the protocol from the domain for use in the image name
BUILD_DATE=`date +%F`
TAG="${BUILD_DATE}_build-${BUILD_NUM}_${COMMIT_HASH}"

export DOCKER_CLI_EXPERIMENTAL=enabled

build_and_tag() {
    echo "$REGISTRY_LOGIN" | docker login $REGISTRY_DOMAIN -u $REGISTRY_USER --password-stdin
    docker buildx build --load --platform linux/amd64 -t $STRIPPED_REGISTRY/$BACKEND_APP_NAME:$TAG -t $STRIPPED_REGISTRY/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
    docker buildx build --load --platform linux/arm64 -t $STRIPPED_REGISTRY/$BACKEND_APP_NAME:$TAG -t $STRIPPED_REGISTRY/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
    docker push --all-tags $STRIPPED_REGISTRY/$BACKEND_APP_NAME
    docker buildx build --load --platform linux/amd64 -t $STRIPPED_REGISTRY/$FRONTEND_APP_NAME:$TAG -t $STRIPPED_REGISTRY/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"
    docker buildx build --load --platform linux/arm64 -t $STRIPPED_REGISTRY/$FRONTEND_APP_NAME:$TAG -t $STRIPPED_REGISTRY/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"
    docker push --all-tags $STRIPPED_REGISTRY/$FRONTEND_APP_NAME
    docker logout
}

echo "Building and Tagging images for $BACKEND_APP_NAME and $FRONTEND_APP_NAME"
build_and_tag
