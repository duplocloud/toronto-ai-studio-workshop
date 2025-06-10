# AWS Workshop - FastAPI Application

A simple FastAPI application with health check and chat endpoints.

## Repo
https://github.com/duplocloud/toronto-ai-studio-workshop


## Table of Contents
- [Python Setup Guide](#python-setup-guide)
- [FastAPI Application](#fastapi-application)
- [ECR Image Push](#ecr-image-push)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Endpoints](#endpoints)

---

# Python Setup Guide

## Creating Virtual Environments

Virtual environments help isolate project dependencies and avoid conflicts between different projects.

### Using venv (Native Python Tool)

The `venv` module is included with Python 3.3+ and is the recommended way to create virtual environments.

#### Create a Virtual Environment

```bash
# Navigate to your project directory
cd /path/to/your/project

# Create virtual environment
python -m venv .venv

# You can also specify a different name
python -m venv myproject_env

# Create with specific Python version (if multiple versions installed)
python3.12 -m venv .venv
```

**What this does:**
- Creates a `.venv` directory (or whatever name you specified)
- Contains a copy of the Python interpreter
- Contains pip for installing packages
- Isolates packages from the global Python installation

## Activating Virtual Environments

### macOS and Linux

```bash
# Activate the virtual environment
source .venv/bin/activate

# Your prompt should change to show (venv) at the beginning
(.venv) $ 
```

### Windows

#### Command Prompt
```cmd
# Activate the virtual environment
.venv\Scripts\activate.bat

# Your prompt should change to show (.venv) at the beginning
(.venv) C:\your\project\path>
```

#### PowerShell
```powershell
# Activate the virtual environment
.venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Your prompt should change to show (venv) at the beginning
(.venv) PS C:\your\project\path>
```

#### Git Bash (Windows)
```bash
# Activate the virtual environment
source .venv/Scripts/activate

# Your prompt should change to show (venv) at the beginning
(venv) $ 
```

## Working with Virtual Environments

### After Activation

Once your virtual environment is activated:

```bash
# Install packages (they'll be installed only in this environment)
pip install fastapi uvicorn

# Install from requirements file
pip install -r requirements.txt

# List installed packages
pip list

# Generate requirements file
pip freeze > requirements.txt

# Upgrade pip
pip install --upgrade pip
```

### Deactivating Virtual Environment

```bash
# Simply run this command (works on all platforms)
deactivate
```

Your prompt should return to normal, indicating you're back in the global Python environment.

## Virtual Environment Best Practices

1. **Create a virtual environment for each project**
2. **Always activate before working on a project**
3. **Keep requirements.txt updated**
4. **Don't commit the virtual environment folder to version control**
5. **Use descriptive names for your virtual environments**

## Troubleshooting

### Common Issues

#### "python: command not found"
- Make sure Python is added to your PATH
- Try using `python3` instead of `python`

#### "venv: command not found"
- Install python3-venv: `sudo apt install python3-venv` (Linux)
- Make sure you're using Python 3.3+

#### PowerShell Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Virtual Environment Not Activating
- Make sure you're in the correct directory
- Check the path to the activation script
- On Windows, try different shells (CMD, PowerShell, Git Bash)

## Python Setup Quick Reference

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Install packages
pip install package_name

# Deactivate
deactivate

# Remove virtual environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

---

# FastAPI Application

## Features

- `/health` - GET endpoint for health checks
- `/chat` - POST endpoint for chat functionality

## Installation

### Step 1: Set Up Python Environment

Follow the [Python Setup Guide](#python-setup-guide) above to install Python and create a virtual environment.

### Step 2: Activate Virtual Environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install directly
pip install fastapi uvicorn

# Or using pyproject.toml
pip install -e .
```

## Running the Application

Start the development server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Endpoints

### Health Check
- **GET** `/health`
- Returns the service health status

Example:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "aws-workshop-api"
}
```

### Chat
- **POST** `/chat`
- Send a message and get a response

Example:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, world!"}'
```

Response:
```json
{
  "response": "You said: Hello, world!",
  "echo": "Hello, world!"
}
```

## Complete Setup and Run Process

Here's the complete process from start to finish:

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate.bat  # Windows CMD

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py

# 4. Test the endpoints
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, FastAPI!"}'
```

## Project Structure

```
aws-workshop/
├── main.py              # FastAPI application
├── requirements.txt     # Project dependencies
├── pyproject.toml      # Project configuration
├── README.md           # This file
├── .python-version     # Python version specification
├── .gitignore          # Git ignore rules
└── venv/               # Virtual environment (created by you)
```

## Next Steps

1. Follow the Python setup guide to install Python
2. Create and activate a virtual environment
3. Install the project dependencies
4. Run the FastAPI application
5. Visit `http://localhost:8000/docs` to explore the interactive API documentation
6. Start building your own endpoints and functionality!

---

# ECR Image Push

This project includes a Python script (`push-to-ecr.py`) to build and push Docker images to Amazon Elastic Container Registry (ECR). This script replaces the original bash script with a more robust Python implementation.

## Features

- **Automated ECR Repository Management**: Creates ECR repository if it doesn't exist
- **Image Building**: Builds Docker images using Podman
- **AWS Authentication**: Handles ECR authentication automatically
- **Error Handling**: Comprehensive error handling with colored output
- **Cross-platform**: Works on macOS, Linux, and Windows

## Prerequisites

### 1. Install Dependencies

Make sure your virtual environment is activated and install the required packages:

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

The script requires:
- `boto3` - AWS SDK for Python
- `botocore` - Low-level AWS client library
- `colorama` - Cross-platform colored terminal output

### 2. AWS Configuration

Ensure you have AWS credentials configured for the specified profile:

```bash
# Configure AWS CLI (if not already done)
aws configure --profile test10

# Or set up credentials file manually at ~/.aws/credentials
[test10]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1
```

### 3. Container Runtime

Install Podman (or Docker):

#### macOS:
```bash
brew install podman
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install podman
```

#### Windows:
Follow the [Podman Windows installation guide](https://podman.io/getting-started/installation#windows)

### 4. Dockerfile

Ensure you have a `Dockerfile` in your project root. Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

## Configuration

The script uses the following default configuration (modify in `push-to-ecr.py` as needed):

```python
VERSION = "v24"                    # Image version tag
REPO_NAME = "ecs-to-eks"          # ECR repository name
REGION = "us-east-1"              # AWS region
PROFILE = "test10"                # AWS profile name
LOCAL_IMAGE = f"localhost/ecs-to-eks:{VERSION}"  # Local image name
```

## Usage

### Basic Usage

Simply run the script from your project directory:

```bash
python push-to-ecr.py
```

### What the Script Does

1. **Builds the Docker Image**: Uses Podman to build your application image
2. **AWS Authentication**: Creates AWS session using the specified profile
3. **Repository Management**: Checks if ECR repository exists, creates it if needed
4. **ECR Authentication**: Authenticates with ECR registry
5. **Image Tagging**: Tags the local image for ECR
6. **Image Push**: Pushes the tagged image to ECR

### Expected Output

```bash
Starting build and ECR push process...
Building image 'localhost/ecs-to-eks:v24'...
Image built successfully.
Getting AWS account ID...
Account ID: 123456789012
Checking if repository 'ecs-to-eks' exists...
Repository 'ecs-to-eks' already exists.
Authenticating with ECR...
Authentication successful.
Checking if local image 'localhost/ecs-to-eks:v24' exists...
Local image found.
Tagging image 'localhost/ecs-to-eks:v24'...
Image tagged successfully.
Pushing image to ECR...
Image pushed successfully!
Image URI: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ecs-to-eks:v24
```

## Customization

### Changing Configuration

You can modify the configuration variables at the top of `push-to-ecr.py`:

```python
# Custom configuration example
VERSION = "v25"                    # Change version
REPO_NAME = "my-app"              # Change repository name
REGION = "us-west-2"              # Change AWS region
PROFILE = "production"            # Change AWS profile
```

### Using Different Container Runtime

To use Docker instead of Podman, replace `podman` commands in the script:

```python
# Change these lines in the script:
run_command(f"docker build -t {LOCAL_IMAGE} .")
run_command(f"docker image exists {LOCAL_IMAGE}")
run_command(f"docker tag {LOCAL_IMAGE} {ecr_image_uri}")
run_command(f"docker push {ecr_image_uri}")
```

## Troubleshooting

### Common Issues

#### "AWS Profile Not Found"
```bash
# Check available profiles
aws configure list-profiles

# Configure the required profile
aws configure --profile test10
```

#### "Podman Command Not Found"
```bash
# Install Podman
brew install podman  # macOS
sudo apt install podman  # Linux
```

#### "Permission Denied" on ECR
- Ensure your AWS credentials have ECR permissions
- Check IAM policies include `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`

#### "Repository Already Exists" Error
- The script handles this automatically, but if you see errors, check repository permissions in AWS Console

### Debug Mode

For more verbose output, you can modify the script to include debug information:

```python
# Add this near the top of push-to-ecr.py for more verbose output
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with CI/CD

You can integrate this script into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Push to ECR
  run: |
    python push-to-ecr.py
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Next Steps

After successfully pushing your image to ECR:

1. **Deploy to ECS**: Use the ECR image URI in your ECS task definitions
2. **Deploy to EKS**: Reference the image in your Kubernetes deployment manifests
3. **Update CI/CD**: Integrate the push script into your deployment pipeline
4. **Monitor**: Set up CloudWatch monitoring for your ECR repositories
