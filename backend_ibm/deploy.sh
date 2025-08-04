#!/bin/bash

# Relativity Backend Deployment Script for IBM Code Engine
# Usage: ./deploy.sh [project_name] [app_name]

set -e

PROJECT_NAME=${1:-"relativity-chatbot"}
APP_NAME=${2:-"relativity-backend"}

echo "🚀 Deploying Relativity Backend to IBM Code Engine"
echo "Project: $PROJECT_NAME"
echo "App: $APP_NAME"

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo "❌ IBM Cloud CLI not found. Please install it first."
    exit 1
fi

# Login to IBM Cloud
echo "🔐 Logging in to IBM Cloud..."
ibmcloud login

# Create or select project
echo "📁 Setting up project..."
if ibmcloud ce project get --name $PROJECT_NAME &> /dev/null; then
    echo "✅ Project $PROJECT_NAME already exists"
    ibmcloud ce project select --name $PROJECT_NAME
else
    echo "📝 Creating project $PROJECT_NAME"
    ibmcloud ce project create --name $PROJECT_NAME
    ibmcloud ce project select --name $PROJECT_NAME
fi

# Build the application
echo "🔨 Building application..."
ibmcloud ce build create --name ${APP_NAME}-build --source .

# Wait for build to complete
echo "⏳ Waiting for build to complete..."
BUILD_STATUS=""
while [ "$BUILD_STATUS" != "Succeeded" ]; do
    BUILD_STATUS=$(ibmcloud ce build get --name ${APP_NAME}-build --output json | jq -r '.status.conditions[0].reason')
    echo "Build status: $BUILD_STATUS"
    sleep 30
done

# Deploy the application
echo "🚀 Deploying application..."
ibmcloud ce app create --name $APP_NAME \
    --image ${APP_NAME}:latest \
    --port 8080 \
    --cpu 1 \
    --memory 2Gi \
    --env IBM_WATSONX_API_KEY="$IBM_WATSONX_API_KEY" \
    --env IBM_WATSONX_PROJECT_ID="$IBM_WATSONX_PROJECT_ID" \
    --env GOOGLE_SHEETS_CREDENTIALS="$GOOGLE_SHEETS_CREDENTIALS" \
    --env ALLOWED_ORIGINS="$ALLOWED_ORIGINS" \
    --env CHATBOT_PORT=8080 \
    --env CHATBOT_HOST=0.0.0.0

# Get the application URL
echo "🔗 Getting application URL..."
APP_URL=$(ibmcloud ce app get --name $APP_NAME --output json | jq -r '.status.url')

echo "✅ Deployment completed successfully!"
echo "🌐 Application URL: $APP_URL"
echo "📊 Health check: $APP_URL/health"
echo ""
echo "📝 Next steps:"
echo "1. Update your Streamlit app with API_BASE_URL=$APP_URL"
echo "2. Test the health endpoint: curl $APP_URL/health"
echo "3. Monitor logs: ibmcloud ce app logs --name $APP_NAME" 