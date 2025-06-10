#!/bin/bash

# Configuration
VERSION=""
ECR_REPOSITORY_NAME="aws-workshop-demo"
AWS_REGION="us-east-1"
LOCAL_CONTAINER_IMAGE="localhost/$ECR_REPOSITORY_NAME:$VERSION"

# Set platform for AWS deployment (always linux/amd64)
PLATFORM="linux/amd64"

echo "Building for AWS platform: $PLATFORM"

# Determine username - use VERSION if set, otherwise parse from VSCODE_PROXY_URI
if [ -n "$VERSION" ]; then
    echo "VERSION is set, using VERSION as username: $VERSION"
    USERNAME="$VERSION"
else

    echo "Using VSCODE_PROXY_URI: $VSCODE_PROXY_URI"

    # Extract username from URL (part before '-vscode')
    USERNAME=$(echo "$VSCODE_PROXY_URI" | sed -n 's/.*:\/\/\([^-]*\)-vscode\..*/\1/p')

    if [ -z "$USERNAME" ]; then
        echo -e "${RED}Error: Could not extract username from URL: $VSCODE_PROXY_URI${NC}"
        exit 1
    fi

    echo "Extracted username from URL: $USERNAME"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting build and ECR push process...${NC}"

# Build the image with platform detection
echo "Building image '$LOCAL_CONTAINER_IMAGE' for platform '$PLATFORM'..."
docker build --platform $PLATFORM -t $LOCAL_CONTAINER_IMAGE .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to build image '$LOCAL_CONTAINER_IMAGE'.${NC}"
    exit 1
fi

echo -e "${GREEN}Image built successfully.${NC}"

# Get AWS account ID
echo "Getting AWS account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to get AWS account ID.${NC}"
    exit 1
fi

echo "Account ID: $ACCOUNT_ID"

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
docker tag $LOCAL_CONTAINER_IMAGE $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$VERSION

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to tag image. Make sure '$LOCAL_CONTAINER_IMAGE' exists.${NC}"
    exit 1
fi

echo -e "${GREEN}Image tagged successfully.${NC}"

# Push the image
echo "Pushing image to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$VERSION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Image pushed successfully!${NC}"
    echo "Image URI: $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$VERSION"
else
    echo -e "${RED}Error: Failed to push image.${NC}"
    exit 1
fi