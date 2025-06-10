#!/bin/bash

# Configuration
VERSION="v25"
ECR_REPOSITORY_NAME="aws-workshop-demo"
AWS_REGION="us-east-1"
#AWS_PROFILE="test10"
LOCAL_CONTAINER_IMAGE="localhost/$ECR_REPOSITORY_NAME:$VERSION"


# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting build and ECR push process...${NC}"

# Build the imagea
echo "Building image '$LOCAL_CONTAINER_IMAGE'..."
podman build -t $LOCAL_CONTAINER_IMAGE .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to build image '$LOCAL_CONTAINER_IMAGE'.${NC}"
    exit 1
fi

echo -e "${GREEN}Image built successfully.${NC}"

# Get AWS account ID
echo "Getting AWS account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to get AWS account ID. Check your profile '$AWS_PROFILE'.${NC}"
    exit 1
fi

echo "Account ID: $ACCOUNT_ID"

# Check if repository exists, create if it doesn't
echo "Checking if repository '$ECR_REPOSITORY_NAME' exists..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION --profile $AWS_PROFILE >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Repository '$ECR_REPOSITORY_NAME' doesn't exist. Creating it...${NC}"
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION --profile $AWS_PROFILE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Repository '$ECR_REPOSITORY_NAME' created successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to create repository '$ECR_REPOSITORY_NAME'.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Repository '$ECR_REPOSITORY_NAME' already exists.${NC}"
fi

# Authenticate with ECR
echo "Authenticating with ECR..."
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | podman login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to authenticate with ECR.${NC}"
    exit 1
fi

echo -e "${GREEN}Authentication successful.${NC}"

# Check if local image exists
echo "Checking if local image '$LOCAL_CONTAINER_IMAGE' exists..."
podman image exists $LOCAL_CONTAINER_IMAGE

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Local image '$LOCAL_CONTAINER_IMAGE' not found. Please build it first.${NC}"
    exit 1
fi

echo -e "${GREEN}Local image found.${NC}"

# Tag the image
echo "Tagging image '$LOCAL_CONTAINER_IMAGE'..."
podman tag $LOCAL_CONTAINER_IMAGE $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$VERSION

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to tag image. Make sure '$LOCAL_CONTAINER_IMAGE' exists.${NC}"
    exit 1
fi

echo -e "${GREEN}Image tagged successfully.${NC}"

# Push the image
echo "Pushing image to ECR..."
podman push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$VERSION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Image pushed successfully!${NC}"
    echo "Image URI: $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$VERSION"
else
    echo -e "${RED}Error: Failed to push image.${NC}"
    exit 1
fi