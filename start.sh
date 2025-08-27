#!/bin/bash

echo "🚀 Starting AI Tools Dashboard..."
echo "📱 The application will be available at: http://localhost:5000"
echo "🔧 Tools included:"
echo "   • Image Filter (Custom 3x3 Convolution)"
echo "   • Image Normalizer (Mean Normalization)" 
echo "   • Token Length Checker (Text Analysis)"
echo "   • Word to One Hot Vector (NLP Encoding)"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and run the app
source .venv/bin/activate && python run.py
