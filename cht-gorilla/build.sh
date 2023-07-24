#!/bin/bash
set -e
export VERSION=1.0.0

IMAGE=ghcr.io/premai-io/chat-gorilla-falcon-7b-gpu
docker buildx build ${@:1} \
    --file ./docker/gpu/Dockerfile \
    --build-arg="MODEL_ID=gorilla-llm/gorilla-falcon-7b-hf-v0" \
    --tag $IMAGE:latest \
    --tag $IMAGE:$VERSION \
    .
docker run --gpus all $IMAGE:$VERSION pytest

IMAGE=ghcr.io/premai-io/chat-gorilla-mpt-7b-gpu
docker buildx build ${@:1} \
    --file ./docker/gpu/Dockerfile \
    --build-arg="MODEL_ID=gorilla-llm/gorilla-mpt-7b-hf-v0" \
    --tag $IMAGE:latest \
    --tag $IMAGE:$VERSION \
    .
docker run --gpus all $IMAGE:$VERSION pytest
