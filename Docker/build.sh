#!/bin/sh

BASEDIR=$(pwd)

#docker build --no-cache -t baardl/piip:$TAG .
IMAGE_TAG=${1:-latest}
#IMAGE_NAME=cantara/ACS
IMAGE_NAME=acs
IMAGE_TITLE="ACS."

echo "Building Docker image $IMAGE_TITLE ($IMAGE_ID) from $BASEDIR."

docker build -t "$IMAGE_NAME:$IMAGE_TAG" "$BASEDIR" --no-cache|| exit 1