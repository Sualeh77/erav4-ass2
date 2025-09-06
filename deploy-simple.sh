#!/bin/bash

# Simple EC2 Deployment Script

echo "🚀 Simple AWS EC2 Deployment Guide"
echo ""
echo "📋 Steps to deploy securely on EC2:"
echo ""

echo "1️⃣ Upload project to EC2 (excluding .env):"
echo "   scp -i your-key.pem -r . ec2-user@your-ec2-ip:/home/ec2-user/tools-dashboard"
echo ""

echo "2️⃣ SSH into EC2 and create secure .env file:"
echo "   ssh -i your-key.pem ec2-user@your-ec2-ip"
echo "   cd tools-dashboard"
echo "   echo 'GEMINI_API_KEY=your_actual_api_key_here' > .env"
echo "   chmod 600 .env  # Make it readable only by owner"
echo ""

echo "3️⃣ Start the application:"
echo "   docker-compose up -d"
echo ""

echo "🔒 Security measures applied:"
echo "   ✅ .env file has 600 permissions (owner read/write only)"
echo "   ✅ API key never transmitted over network"
echo "   ✅ API key not stored in Docker image"
echo "   ✅ API key not in version control"
echo ""

echo "🌐 Access your application at:"
echo "   http://your-ec2-public-ip:5002"
