#!/usr/bin/env bash
set -euo pipefail


REGION=${REGION:-us-east-1}
ACCOUNT_ID=${ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}
REPO_NAME=${REPO_NAME:-crud-api}
TAG=${TAG:-v1}


aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" >/dev/null 2>&1 || \
aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION" >/dev/null


ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"


docker build -t "$REPO_NAME:$TAG" ./app


docker tag "$REPO_NAME:$TAG" "$ECR_URI:$TAG"
docker push "$ECR_URI:$TAG"


echo "IMAGE_URI=$ECR_URI:$TAG"