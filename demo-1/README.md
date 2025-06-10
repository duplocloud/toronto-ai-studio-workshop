# Demo 1 - AWS Workshop

## Overview
This is the first demonstration in the AWS workshop series.

## Prerequisites
- Python 3.x installed
- AWS CLI configured
- Required AWS permissions

## Getting Started
1. Navigate to this directory
2. Install dependencies (if any)
3. Run the demo:
   ```bash
   python start.py
   ```

## Running the Application
The application will start on **port 8001** with the following endpoints:
- Health check: http://localhost:8001/health
- Chat endpoint: http://localhost:8001/chat
- API documentation: http://localhost:8001/docs
- Alternative docs: http://localhost:8001/redoc

## Testing the API

### Health Check
```bash
curl http://localhost:8001/health
```

### Chat Endpoint
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, world!"}'
```

## What This Demo Covers
- [Add specific topics covered in this demo]
- [Add learning objectives]

## Resources
- [Add relevant AWS documentation links]
- [Add any additional resources]

## Next Steps
Proceed to Demo 2 after completing this demonstration. 