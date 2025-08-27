#!/usr/bin/env python3
"""
Production Docker run script for the Flask Tools Dashboard
"""

import os
from main import app

def get_config():
    """Get configuration based on environment"""
    config = {
        'debug': os.getenv('FLASK_ENV', 'production') == 'development',
        'host': '0.0.0.0',
        'port': int(os.getenv('PORT', 5002)),
        'threaded': True
    }
    return config

if __name__ == "__main__":
    config = get_config()
    
    print("🐳 Starting Tools Dashboard in Docker container...")
    print(f"🌐 Server will be available at: http://localhost:{config['port']}")
    print(f"🔧 Environment: {'Development' if config['debug'] else 'Production'}")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    app.run(**config)
