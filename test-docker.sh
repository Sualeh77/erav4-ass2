#!/bin/bash

echo "🧪 Testing Docker deployment..."
echo ""

# Start the application
echo "📦 Starting Docker container..."
docker-compose up -d

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Test main page
echo "🏠 Testing main page..."
if curl -f -s http://localhost:5002/ > /dev/null; then
    echo "✅ Main page: OK"
else
    echo "❌ Main page: FAILED"
    exit 1
fi

# Test tool pages
echo "🛠️ Testing tool pages..."

# Image Filter
if curl -f -s http://localhost:5002/image-filter/ > /dev/null; then
    echo "✅ Image Filter: OK"
else
    echo "❌ Image Filter: FAILED"
fi

# Image Normalizer
if curl -f -s http://localhost:5002/image-normalizer/ > /dev/null; then
    echo "✅ Image Normalizer: OK"
else
    echo "❌ Image Normalizer: FAILED"
fi

# Token Checker
if curl -f -s http://localhost:5002/token-checker/ > /dev/null; then
    echo "✅ Token Checker: OK"
else
    echo "❌ Token Checker: FAILED"
fi

# One Hot Vector
if curl -f -s http://localhost:5002/one-hot-vector/ > /dev/null; then
    echo "✅ One Hot Vector: OK"
else
    echo "❌ One Hot Vector: FAILED"
fi

echo ""
echo "🎉 All tests completed!"
echo "📱 Application is running at: http://localhost:5002"
echo ""
echo "To stop the application, run: docker-compose down"
