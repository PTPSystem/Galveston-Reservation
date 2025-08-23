#!/bin/bash
# staging_deploy.sh - Deploy staging environment for testing security changes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STAGING_PORT=8081
STAGING_DB_PORT=5433
STAGING_ENV_FILE=".env.staging"

echo -e "${GREEN}🚀 Deploying Galveston Reservation System - STAGING Environment${NC}"
echo "========================================================================="

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
        return 0
    fi
}

# Function to create staging environment file if missing
create_staging_env() {
    if [ ! -f "$STAGING_ENV_FILE" ]; then
        echo -e "${YELLOW}📄 Creating staging environment file...${NC}"
        cat > "$STAGING_ENV_FILE" << EOF
# Staging Environment Configuration
FLASK_ENV=staging
DEBUG=true
SECRET_KEY=staging-secret-key-replace-with-32-char-random-string
APPROVAL_TOKEN_SECRET=staging-approval-secret-replace-with-32-char-random

# Database
DATABASE_URL=postgresql+psycopg2://app_staging:staging_pass@db-staging:5432/galveston_staging

# Email Configuration (use test email accounts)
BOOKING_APPROVAL_EMAIL=staging-admin@yourdomain.com
BOOKING_NOTIFICATION_EMAILS=staging-notifications@yourdomain.com

# Application URLs
BASE_URL=http://83.229.35.162:8081

# SMTP (configure with test email service)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-staging-email@gmail.com
SMTP_PASSWORD=your-staging-app-password
SMTP_USE_TLS=true

# Google Calendar (optional for staging)
GOOGLE_CALENDAR_ID=your-staging-calendar@gmail.com
GOOGLE_CREDENTIALS_PATH=/run/secrets/service-account-staging.json

# Security
CSRF_SECRET_KEY=staging-csrf-secret-32-char-random-string
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true

# Logging
LOG_LEVEL=DEBUG
EOF
        echo -e "${GREEN}✅ Created $STAGING_ENV_FILE${NC}"
        echo -e "${YELLOW}⚠️  Please edit $STAGING_ENV_FILE with your staging credentials${NC}"
    else
        echo -e "${GREEN}✅ Staging environment file exists${NC}"
    fi
}

# Function to create secrets directory for staging
create_staging_secrets() {
    if [ ! -d "secrets" ]; then
        mkdir -p secrets
        echo -e "${GREEN}✅ Created secrets directory${NC}"
    fi
    
    if [ ! -f "secrets/service-account-staging.json" ]; then
        echo -e "${YELLOW}⚠️  Google service account file for staging not found${NC}"
        echo "   Please place your staging Google service account JSON at:"
        echo "   secrets/service-account-staging.json"
        echo "   (Optional - system will work without Google Calendar integration)"
    fi
}

# Pre-deployment checks
echo -e "${YELLOW}🔍 Running pre-deployment checks...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is available${NC}"

# Check ports
echo -e "${YELLOW}🔍 Checking port availability...${NC}"
if ! check_port $STAGING_PORT; then
    echo -e "${RED}❌ Staging web port $STAGING_PORT is in use${NC}"
    echo "   Stop the service using this port or choose a different port"
    exit 1
fi

if ! check_port $STAGING_DB_PORT; then
    echo -e "${RED}❌ Staging database port $STAGING_DB_PORT is in use${NC}"
    echo "   Stop the service using this port or choose a different port"
    exit 1
fi

# Create staging configuration
create_staging_env
create_staging_secrets

# Build and deploy staging
echo -e "${YELLOW}🏗️  Building staging environment...${NC}"

# Stop any existing staging containers
echo -e "${YELLOW}🛑 Stopping existing staging containers...${NC}"
docker-compose -f compose.staging.yaml down --remove-orphans || true

# Build staging image
echo -e "${YELLOW}🔨 Building staging Docker image...${NC}"
docker-compose -f compose.staging.yaml build --no-cache

# Start staging environment
echo -e "${YELLOW}🚀 Starting staging environment...${NC}"
docker-compose -f compose.staging.yaml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if docker-compose -f compose.staging.yaml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Staging environment deployed successfully!${NC}"
    echo ""
    echo "🌐 Access your staging environment at:"
    echo "   http://83.229.35.162:$STAGING_PORT"
    echo ""
    echo "📊 Database connection (for debugging):"
    echo "   Host: 83.229.35.162"
    echo "   Port: $STAGING_DB_PORT"
    echo "   Database: galveston_staging"
    echo "   User: app_staging"
    echo ""
    echo "🔍 Monitor logs with:"
    echo "   docker-compose -f compose.staging.yaml logs -f"
    echo ""
    echo "🛑 Stop staging with:"
    echo "   docker-compose -f compose.staging.yaml down"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Test your security changes thoroughly before production deployment!${NC}"
else
    echo -e "${RED}❌ Failed to start staging environment${NC}"
    echo "Check logs with: docker-compose -f compose.staging.yaml logs"
    exit 1
fi
