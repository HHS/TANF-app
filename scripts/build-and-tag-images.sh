#!/bin/bash
set -euo pipefail

# Validate environment variables 
: "${BACKEND_APP_NAME:?Missing BACKEND_APP_NAME}"
: "${FRONTEND_APP_NAME:?Missing FRONTEND_APP_NAME}"
: "${BACKEND_PATH:?Missing BACKEND_PATH}"
: "${FRONTEND_PATH:?Missing FRONTEND_PATH}"
: "${BUILD_NUM:?Missing BUILD_NUM}"
: "${COMMIT_HASH:?Missing COMMIT_HASH}"
: "${REGISTRY_LOGIN:?Missing REGISTRY_LOGIN}"
: "${REGISTRY_USER:?Missing REGISTRY_USER}"
: "${REGISTRY_DOMAIN:?Missing REGISTRY_DOMAIN}"
: "${REPOSISTORY_OWNER:?Missing REPOSISTORY_OWNER}"

STRIPPED_REGISTRY="${REGISTRY_DOMAIN#*://}" # removes the protocol from the domain for use in the image name
IMAGE_ID="${STRIPPED_REGISTRY}/${REPOSISTORY_OWNER}"
BUILD_DATE=`date +%F`
TAG="${BUILD_DATE}_build-${BUILD_NUM}_${COMMIT_HASH}"

export DOCKER_CLI_EXPERIMENTAL=enabled

build_and_tag() {
    echo "$REGISTRY_LOGIN" | docker login $REGISTRY_DOMAIN -u $REGISTRY_USER --password-stdin
    docker buildx build --load --platform linux/amd64 -t $IMAGE_ID/$BACKEND_APP_NAME:$TAG -t $IMAGE_ID/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
    docker buildx build --load --platform linux/arm64 -t $IMAGE_ID/$BACKEND_APP_NAME:$TAG -t $IMAGE_ID/$BACKEND_APP_NAME:latest "$BACKEND_PATH"
    docker push --all-tags $IMAGE_ID/$BACKEND_APP_NAME
    docker buildx build --load --platform linux/amd64 -t $IMAGE_ID/$FRONTEND_APP_NAME:$TAG -t $IMAGE_ID/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"
    docker buildx build --load --platform linux/arm64 -t $IMAGE_ID/$FRONTEND_APP_NAME:$TAG -t $IMAGE_ID/$FRONTEND_APP_NAME:latest "$FRONTEND_PATH"
    docker push --all-tags $IMAGE_ID/$FRONTEND_APP_NAME
    docker logout
}

echo "Building and Tagging images for $BACKEND_APP_NAME and $FRONTEND_APP_NAME"
build_and_tag
