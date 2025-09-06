from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
import tempfile

# Import our tool modules
from image_filter_demo.image_filter import image_filter_bp
from image_normalizer.image_normalizer import image_normalizer_bp
from token_length_checker.token_checker import token_checker_bp
from word_to_one_hot_vector.one_hot_vector import one_hot_vector_bp
from cnn_visualizer.cnn_visualizer import cnn_visualizer_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Register blueprints
app.register_blueprint(image_filter_bp, url_prefix='/image-filter')
app.register_blueprint(image_normalizer_bp, url_prefix='/image-normalizer')
app.register_blueprint(token_checker_bp, url_prefix='/token-checker')
app.register_blueprint(one_hot_vector_bp, url_prefix='/one-hot-vector')
app.register_blueprint(cnn_visualizer_bp, url_prefix='/cnn-visualizer')

@app.route('/')
def index():
    """Main page with navigation to all tools"""
    return render_template('index.html')

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Please upload a smaller image.')
    return redirect(request.url)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
