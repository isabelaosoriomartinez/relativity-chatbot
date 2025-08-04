# Deploy to IBM Code Engine

This guide will help you deploy the Relativity FAQ chatbot to IBM Code Engine using Docker containers.

## Prerequisites

1. IBM Cloud account
2. IBM CLI installed and configured
3. Docker installed locally
4. Container Registry access

## Step 1: Set Up IBM Cloud Environment

### Install IBM CLI
```bash
# Download and install IBM CLI
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh

# Login to IBM Cloud
ibmcloud login

# Set target region
ibmcloud target -r us-south

# Install Code Engine plugin
ibmcloud plugin install code-engine
```

### Create IBM Cloud Project
```bash
# Create a new project
ibmcloud ce project create --name relativity-chatbot-project

# Set the project as target
ibmcloud ce project target --name relativity-chatbot-project
```

## Step 2: Set Up Container Registry

### Create Container Registry Namespace
```bash
# Create a namespace for your images
ibmcloud cr namespace-add relativity-chatbot-namespace

# Set the registry region
ibmcloud cr region-set us-south
```

### Build and Push Docker Images

```bash
# Build the Docker image
docker build -t us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest .

# Login to IBM Container Registry
ibmcloud cr login

# Push the image
docker push us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest
```

## Step 3: Configure Environment Variables

### Create Environment Variables in Code Engine
```bash
# Create environment variables for the application
ibmcloud ce env create --name IBM_WATSONX_API_KEY --value "your_ibm_watsonx_api_key"
ibmcloud ce env create --name IBM_WATSONX_PROJECT_ID --value "your_ibm_watsonx_project_id"
ibmcloud ce env create --name GOOGLE_SHEETS_CREDENTIALS_PATH --value "/app/credentials.json"
ibmcloud ce env create --name GOOGLE_SHEET_ID --value "your_google_sheet_id"
ibmcloud ce env create --name CHATBOT_PORT --value "5000"
ibmcloud ce env create --name CHATBOT_HOST --value "0.0.0.0"
```

## Step 4: Deploy Backend Service

### Create Backend Application
```bash
# Deploy the Flask backend
ibmcloud ce app create \
  --name relativity-chatbot-backend \
  --image us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest \
  --port 5000 \
  --cpu 1 \
  --memory 2Gi \
  --min-scale 1 \
  --max-scale 3 \
  --env IBM_WATSONX_API_KEY \
  --env IBM_WATSONX_PROJECT_ID \
  --env GOOGLE_SHEETS_CREDENTIALS_PATH \
  --env GOOGLE_SHEET_ID \
  --env CHATBOT_PORT \
  --env CHATBOT_HOST \
  --command "python app.py"
```

### Create Frontend Application
```bash
# Deploy the Gradio frontend
ibmcloud ce app create \
  --name relativity-chatbot-frontend \
  --image us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest \
  --port 7860 \
  --cpu 0.5 \
  --memory 1Gi \
  --min-scale 1 \
  --max-scale 2 \
  --env BACKEND_URL \
  --command "python frontend.py"
```

## Step 5: Set Up Data Ingestion

### Create Data Ingestion Job
```bash
# Create a job for data ingestion
ibmcloud ce job create \
  --name relativity-data-ingestion \
  --image us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest \
  --cpu 1 \
  --memory 2Gi \
  --env IBM_WATSONX_API_KEY \
  --env IBM_WATSONX_PROJECT_ID \
  --command "python ingest.py"
```

### Run Data Ingestion
```bash
# Run the data ingestion job
ibmcloud ce jobrun submit --job relativity-data-ingestion
```

## Step 6: Configure Networking

### Set Up Service Binding
```bash
# Bind the frontend to the backend service
ibmcloud ce app bind --name relativity-chatbot-frontend --service-instance relativity-chatbot-backend
```

### Configure Environment Variables for Frontend
```bash
# Set the backend URL for the frontend
ibmcloud ce app update --name relativity-chatbot-frontend --env BACKEND_URL=https://relativity-chatbot-backend.your-project.us-south.codeengine.appdomain.cloud
```

## Step 7: Set Up Persistent Storage (Optional)

### Create Persistent Volume
```bash
# Create a persistent volume for the vector store
ibmcloud ce volume create \
  --name relativity-chroma-db \
  --size 10Gi \
  --access-mode ReadWriteMany
```

### Mount Volume to Applications
```bash
# Mount volume to backend
ibmcloud ce app update --name relativity-chatbot-backend --mount /app/chroma_db=relativity-chroma-db

# Mount volume to frontend
ibmcloud ce app update --name relativity-chatbot-frontend --mount /app/chroma_db=relativity-chroma-db
```

## Step 8: Configure Secrets

### Store Google Sheets Credentials
```bash
# Create a secret for Google Sheets credentials
ibmcloud ce secret create \
  --name google-sheets-credentials \
  --from-file credentials.json=path/to/your/service-account.json
```

### Mount Secret to Applications
```bash
# Mount secret to backend
ibmcloud ce app update --name relativity-chatbot-backend --mount /app/credentials.json=google-sheets-credentials:credentials.json
```

## Step 9: Set Up Monitoring and Logging

### Enable Application Logging
```bash
# View application logs
ibmcloud ce app logs --name relativity-chatbot-backend --follow
ibmcloud ce app logs --name relativity-chatbot-frontend --follow
```

### Set Up Monitoring
```bash
# Create monitoring dashboard
ibmcloud ce app events --name relativity-chatbot-backend
ibmcloud ce app events --name relativity-chatbot-frontend
```

## Step 10: Test the Deployment

### Check Application Status
```bash
# List all applications
ibmcloud ce app list

# Get application details
ibmcloud ce app get --name relativity-chatbot-backend
ibmcloud ce app get --name relativity-chatbot-frontend
```

### Test Health Endpoint
```bash
# Test backend health
curl https://relativity-chatbot-backend.your-project.us-south.codeengine.appdomain.cloud/health
```

## Step 11: Set Up Custom Domain (Optional)

### Configure Custom Domain
```bash
# Add custom domain
ibmcloud ce domain create \
  --name relativity-chatbot.yourdomain.com \
  --app relativity-chatbot-frontend
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # Check image exists
   ibmcloud cr images
   
   # Rebuild and push if needed
   docker build -t us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest .
   docker push us.icr.io/relativity-chatbot-namespace/relativity-chatbot:latest
   ```

2. **Environment Variable Issues**
   ```bash
   # List environment variables
   ibmcloud ce env list
   
   # Update environment variables
   ibmcloud ce env update --name IBM_WATSONX_API_KEY --value "new_value"
   ```

3. **Application Startup Issues**
   ```bash
   # Check application logs
   ibmcloud ce app logs --name relativity-chatbot-backend --tail 100
   
   # Restart application
   ibmcloud ce app restart --name relativity-chatbot-backend
   ```

### Performance Optimization

1. **Scale Applications**
   ```bash
   # Scale backend
   ibmcloud ce app update --name relativity-chatbot-backend --max-scale 5
   
   # Scale frontend
   ibmcloud ce app update --name relativity-chatbot-frontend --max-scale 3
   ```

2. **Resource Allocation**
   ```bash
   # Increase CPU and memory
   ibmcloud ce app update --name relativity-chatbot-backend --cpu 2 --memory 4Gi
   ```

## Maintenance

### Update Application
```bash
# Build new image
docker build -t us.icr.io/relativity-chatbot-namespace/relativity-chatbot:v2 .

# Push new image
docker push us.icr.io/relativity-chatbot-namespace/relativity-chatbot:v2

# Update application
ibmcloud ce app update --name relativity-chatbot-backend --image us.icr.io/relativity-chatbot-namespace/relativity-chatbot:v2
```

### Backup Data
```bash
# Export vector store data
ibmcloud ce jobrun submit --job relativity-data-backup
```

### Monitor Costs
```bash
# Check resource usage
ibmcloud ce app list
ibmcloud ce job list
```

## Security Considerations

1. **API Key Management**: Use IBM Cloud Secrets Manager for sensitive data
2. **Network Security**: Configure VPC and security groups
3. **Access Control**: Use IAM roles and permissions
4. **Data Encryption**: Enable encryption at rest and in transit

## Cost Optimization

1. **Right-size Resources**: Monitor usage and adjust CPU/memory
2. **Auto-scaling**: Set appropriate min/max scale values
3. **Scheduled Jobs**: Use jobs for batch processing instead of always-on services
4. **Resource Cleanup**: Delete unused resources regularly 