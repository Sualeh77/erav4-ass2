#!/bin/bash

# AWS Deployment Script with Secure API Key Management

echo "🚀 Deploying Tools Dashboard to AWS EC2..."

# Method 1: Using AWS Systems Manager Parameter Store
echo "📋 Setting up AWS Parameter Store..."

# Store your API key in AWS Parameter Store (run this once)
aws ssm put-parameter \
    --name "/tools-dashboard/gemini-api-key" \
    --value "your_actual_gemini_api_key_here" \
    --type "SecureString" \
    --description "Gemini API key for Tools Dashboard"

# Create docker-compose override for AWS
cat > docker-compose.aws.yml << 'EOF'
services:
  tools-dashboard:
    environment:
      - FLASK_ENV=production
      - FLASK_APP=main.py
      - PYTHONPATH=/app
      # API key will be retrieved from AWS Parameter Store
    volumes:
      - temp_files:/tmp
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

volumes:
  temp_files:
    driver: local

networks:
  tools-network:
    driver: bridge
EOF

# Create startup script that retrieves API key from Parameter Store
cat > start-with-secrets.sh << 'EOF'
#!/bin/bash

echo "🔐 Retrieving API key from AWS Parameter Store..."

# Get API key from AWS Parameter Store
export GEMINI_API_KEY=$(aws ssm get-parameter \
    --name "/tools-dashboard/gemini-api-key" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text)

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Failed to retrieve API key from Parameter Store"
    exit 1
fi

echo "✅ API key retrieved successfully"
echo "🚀 Starting application..."

# Start the application with the retrieved API key
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d

echo "🎉 Application started successfully!"
echo "📱 Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5002"
EOF

chmod +x start-with-secrets.sh

echo "✅ AWS deployment files created!"
echo ""
echo "📋 Next steps:"
echo "1. Upload project to EC2: scp -r . ec2-user@your-instance:/home/ec2-user/tools-dashboard"
echo "2. SSH into EC2 and run: ./start-with-secrets.sh"
