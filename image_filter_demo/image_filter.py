from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os
import io
import base64

image_filter_bp = Blueprint('image_filter', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_convolution(image_array, kernel):
    """Apply convolution with the given kernel to the image"""
    # Convert to grayscale if needed
    if len(image_array.shape) == 3:
        image_array = np.dot(image_array[...,:3], [0.2989, 0.5870, 0.1140])
    
    height, width = image_array.shape
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2
    
    # Pad the image
    padded_image = np.pad(image_array, ((pad, pad), (pad, pad)), mode='edge')
    
    # Apply convolution
    output = np.zeros_like(image_array)
    
    for i in range(height):
        for j in range(width):
            region = padded_image[i:i+kernel_size, j:j+kernel_size]
            output[i, j] = np.sum(region * kernel)
    
    # Normalize output to 0-255 range
    output = np.clip(output, 0, 255)
    return output.astype(np.uint8)

def array_to_base64(image_array):
    """Convert numpy array to base64 string for display"""
    if len(image_array.shape) == 2:
        # Grayscale
        img = Image.fromarray(image_array, mode='L')
    else:
        # RGB
        img = Image.fromarray(image_array, mode='RGB')
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    encoded_img = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_img}"

@image_filter_bp.route('/')
def index():
    return render_template('image_filter/index.html')

@image_filter_bp.route('/upload', methods=['POST'])
def upload_and_filter():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('image_filter.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('image_filter.index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload an image file.')
        return redirect(url_for('image_filter.index'))
    
    try:
        # Get kernel values from form
        kernel_values = []
        for i in range(9):  # 3x3 kernel
            value = request.form.get(f'kernel_{i}', '0')
            try:
                kernel_values.append(float(value))
            except ValueError:
                kernel_values.append(0.0)
        
        kernel = np.array(kernel_values).reshape(3, 3)
        
        # Process image
        image = Image.open(file.stream)
        image_array = np.array(image)
        
        # Apply convolution
        filtered_array = apply_convolution(image_array, kernel)
        
        # Convert to base64 for display
        original_b64 = array_to_base64(image_array)
        filtered_b64 = array_to_base64(filtered_array)
        
        return render_template('image_filter/result.html', 
                             original_image=original_b64,
                             filtered_image=filtered_b64,
                             kernel=kernel.tolist(),
                             filename=secure_filename(file.filename))
    
    except Exception as e:
        flash(f'Error processing image: {str(e)}')
        return redirect(url_for('image_filter.index'))
