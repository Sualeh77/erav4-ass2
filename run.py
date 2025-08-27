#!/usr/bin/env python3
"""
Run script for the Flask AI Tools Dashboard
"""

from main import app

if __name__ == "__main__":
    print("🚀 Starting AI Tools Dashboard...")
    print("📱 Access the application at: http://localhost:5000")
    print("🔧 Tools available:")
    print("   • Image Filter (Custom 3x3 Convolution)")
    print("   • Image Normalizer (Mean Normalization)")
    print("   • Token Length Checker (Text Analysis)")
    print("   • Word to One Hot Vector (NLP Encoding)")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
