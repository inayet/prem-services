#!/bin/bash
set -e
export VERSION=1.0.3

IMAGE=ghcr.io/premai-io/chat-dolly-v2-12b-gpu
docker buildx build ${@:1} \
    --file ./docker/gpu/Dockerfile \
    --build-arg="MODEL_ID=databricks/dolly-v2-12b" \
    --tag $IMAGE:latest \
    --tag $IMAGE:$VERSION \
    .
docker run --gpus all $IMAGE:$VERSION pytest
