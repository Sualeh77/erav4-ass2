from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import io
import base64

image_normalizer_bp = Blueprint('image_normalizer', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_image(image_array):
    """Apply mean normalization to the image"""
    # Convert to float for calculations
    image_float = image_array.astype(np.float32)
    
    # Calculate mean for each channel
    if len(image_float.shape) == 3:  # RGB image
        means = np.mean(image_float, axis=(0, 1))
        normalized = image_float - means
    else:  # Grayscale image
        mean = np.mean(image_float)
        normalized = image_float - mean
    
    # Normalize to 0-255 range for display
    # Find min and max values
    min_val = np.min(normalized)
    max_val = np.max(normalized)
    
    if max_val - min_val > 0:
        normalized = ((normalized - min_val) / (max_val - min_val)) * 255
    else:
        normalized = np.zeros_like(normalized)
    
    return normalized.astype(np.uint8), means if len(image_float.shape) == 3 else mean

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

@image_normalizer_bp.route('/')
def index():
    return render_template('image_normalizer/index.html')

@image_normalizer_bp.route('/upload', methods=['POST'])
def upload_and_normalize():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('image_normalizer.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('image_normalizer.index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload an image file.')
        return redirect(url_for('image_normalizer.index'))
    
    try:
        # Process image
        image = Image.open(file.stream)
        
        # Convert to RGB if needed
        if image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
        
        image_array = np.array(image)
        
        # Apply normalization
        normalized_array, means = normalize_image(image_array)
        
        # Calculate statistics
        original_stats = {
            'mean': np.mean(image_array, axis=(0, 1)) if len(image_array.shape) == 3 else np.mean(image_array),
            'std': np.std(image_array, axis=(0, 1)) if len(image_array.shape) == 3 else np.std(image_array),
            'min': np.min(image_array, axis=(0, 1)) if len(image_array.shape) == 3 else np.min(image_array),
            'max': np.max(image_array, axis=(0, 1)) if len(image_array.shape) == 3 else np.max(image_array)
        }
        
        normalized_stats = {
            'mean': np.mean(normalized_array, axis=(0, 1)) if len(normalized_array.shape) == 3 else np.mean(normalized_array),
            'std': np.std(normalized_array, axis=(0, 1)) if len(normalized_array.shape) == 3 else np.std(normalized_array),
            'min': np.min(normalized_array, axis=(0, 1)) if len(normalized_array.shape) == 3 else np.min(normalized_array),
            'max': np.max(normalized_array, axis=(0, 1)) if len(normalized_array.shape) == 3 else np.max(normalized_array)
        }
        
        # Convert to base64 for display
        original_b64 = array_to_base64(image_array)
        normalized_b64 = array_to_base64(normalized_array)
        
        return render_template('image_normalizer/result.html', 
                             original_image=original_b64,
                             normalized_image=normalized_b64,
                             original_stats=original_stats,
                             normalized_stats=normalized_stats,
                             subtracted_means=means,
                             filename=secure_filename(file.filename),
                             is_color=len(image_array.shape) == 3)
    
    except Exception as e:
        flash(f'Error processing image: {str(e)}')
        return redirect(url_for('image_normalizer.index'))
