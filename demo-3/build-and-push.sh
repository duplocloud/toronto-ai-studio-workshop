#!/bin/bash

# Configuration
VERSION="-demo3"
ECR_REPOSITORY_NAME="agents"
AWS_REGION="us-east-1"
ACCOUNT_ID="$(aws sts get-caller-identity --query "Account" --output text)"

# Extract username from VSCODE_PROXY_URI and append version if set
echo "Using VSCODE_PROXY_URI: $VSCODE_PROXY_URI"

# Extract username from URL (part before '-vscode')
BASE_USERNAME=$(echo "$VSCODE_PROXY_URI" | sed -n 's/.*:\/\/\([^-]*\)-vscode\..*/\1/p')

if [ -z "$BASE_USERNAME" ]; then
    echo -e "${RED}Error: Could not extract username from URL: $VSCODE_PROXY_URI${NC}"
    exit 1
fi

echo "Extracted base username from URL: $BASE_USERNAME"

# Append version to username if VERSION is set
if [ -n "$VERSION" ]; then
    USERNAME="${BASE_USERNAME}-${VERSION}"
    echo "VERSION is set, appending to username: $USERNAME"
else
    USERNAME="$BASE_USERNAME"
    echo "No VERSION set, using base username: $USERNAME"
fi

# Set local container image name using USERNAME
LOCAL_CONTAINER_IMAGE="localhost/$ECR_REPOSITORY_NAME:$USERNAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting build and ECR push process...${NC}"

# Build the image with platform detection
echo "Building image '$LOCAL_CONTAINER_IMAGE' for platform '$PLATFORM'..."
docker build -t $LOCAL_CONTAINER_IMAGE .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to build image '$LOCAL_CONTAINER_IMAGE'.${NC}"
    exit 1
fi

echo -e "${GREEN}Image built successfully.${NC}"

# Authenticate with ECR
echo "Authenticating with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to authenticate with ECR.${NC}"
    exit 1
fi

echo -e "${GREEN}Authentication successful.${NC}"

# Check if local image exists
echo "Checking if local image '$LOCAL_CONTAINER_IMAGE' exists..."
docker image inspect $LOCAL_CONTAINER_IMAGE >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Local image '$LOCAL_CONTAINER_IMAGE' not found. Please build it first.${NC}"
    exit 1
fi

echo -e "${GREEN}Local image found.${NC}"

# Tag the image
echo "Tagging image '$LOCAL_CONTAINER_IMAGE'..."
docker tag $LOCAL_CONTAINER_IMAGE $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$USERNAME

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to tag image. Make sure '$LOCAL_CONTAINER_IMAGE' exists.${NC}"
    exit 1
fi

echo -e "${GREEN}Image tagged successfully.${NC}"

# Push the image
echo "Pushing image to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$USERNAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Image pushed successfully!${NC}"
    echo "Image URI: $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$USERNAME"
else
    echo -e "${RED}Error: Failed to push image.${NC}"
    exit 1
fi