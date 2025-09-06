from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import io
import base64
import os
from dotenv import load_dotenv
import google.genai as genai
import openai
import requests
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

cnn_visualizer_bp = Blueprint('cnn_visualizer', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Configure AI APIs
try:
    # Gemini for text descriptions
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    model = 'gemini-2.0-flash-exp'
except Exception as e:
    print(f"Warning: Could not configure Gemini API: {e}")
    client = None
    model = None

try:
    # OpenAI for image generation
    openai.api_key = os.getenv('OPENAI_API_KEY')
    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except Exception as e:
    print(f"Warning: Could not configure OpenAI API: {e}")
    openai_client = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def get_cnn_block_prompt(block_number, image_description):
    """Generate prompts for each CNN block"""
    prompts = {
        1: f"""
        You are an expert in Convolutional Neural Networks. I have an image: {image_description}
        
        Generate a detailed description of how this image would look after passing through the FIRST BLOCK of a CNN (typically 2-3 convolutional layers).
        
        The first block typically:
        - Detects edges, lines, and basic gradients
        - Captures low-level features like horizontal/vertical edges
        - Has small receptive fields
        - Shows high contrast boundaries and simple patterns
        
        Describe the visual transformation in detail, focusing on:
        1. What edges and gradients would be highlighted
        2. How the image would appear (more edge-focused, high contrast)
        3. What basic patterns would emerge
        
        Keep the description vivid and technical but accessible.
        """,
        
        2: f"""
        You are an expert in Convolutional Neural Networks. I have an image: {image_description}
        
        Generate a detailed description of how this image would look after passing through the SECOND BLOCK of a CNN.
        
        The second block typically:
        - Combines edges to form patterns and textures
        - Detects corners, curves, and simple shapes
        - Shows texture patterns like stripes, dots, or rough/smooth surfaces
        - Has larger receptive fields than block 1
        
        Describe the visual transformation in detail, focusing on:
        1. What patterns and textures would be emphasized
        2. How simple shapes and curves would appear
        3. What texture information would be captured
        
        Keep the description vivid and technical but accessible.
        """,
        
        3: f"""
        You are an expert in Convolutional Neural Networks. I have an image: {image_description}
        
        Generate a detailed description of how this image would look after passing through the THIRD BLOCK of a CNN.
        
        The third block typically:
        - Combines patterns to identify parts of objects
        - Detects object parts like eyes, wheels, leaves, etc.
        - Shows meaningful object components
        - Has even larger receptive fields
        
        Describe the visual transformation in detail, focusing on:
        1. What object parts would be highlighted
        2. How recognizable components would appear
        3. What meaningful structures would emerge
        
        Keep the description vivid and technical but accessible.
        """,
        
        4: f"""
        You are an expert in Convolutional Neural Networks. I have an image: {image_description}
        
        Generate a detailed description of how this image would look after passing through the FOURTH BLOCK of a CNN.
        
        The fourth block typically:
        - Combines object parts to recognize complete objects
        - Shows high-level semantic understanding
        - Captures full object representations
        - Has the largest receptive fields
        
        Describe the visual transformation in detail, focusing on:
        1. What complete objects would be recognized
        2. How the full semantic understanding would appear
        3. What high-level features would be captured
        
        Keep the description vivid and technical but accessible.
        """
    }
    
    return prompts.get(block_number, "Invalid block number")

def generate_cnn_visualization(image_description, block_number):
    """Generate CNN visualization description using Gemini"""
    if not client or not model:
        return "Error: Gemini API not configured. Please check your API key."
    
    try:
        prompt = get_cnn_block_prompt(block_number, image_description)
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating visualization: {str(e)}"

def analyze_image_content(image):
    """Analyze image content to provide context for CNN visualization"""
    if not client or not model:
        return "Image uploaded"
    
    try:
        # For now, return a simple description since image analysis requires more complex setup
        # In a production environment, you'd implement proper image-to-text functionality
        return "Image uploaded successfully. Click on the CNN blocks below to see how this image would transform through different layers of a Convolutional Neural Network."
    except Exception as e:
        return f"Image analysis error: {str(e)}"

@cnn_visualizer_bp.route('/')
def index():
    return render_template('cnn_visualizer/index.html')

@cnn_visualizer_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('cnn_visualizer.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('cnn_visualizer.index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload an image file.')
        return redirect(url_for('cnn_visualizer.index'))
    
    try:
        # Process image
        image = Image.open(file.stream)
        
        # Convert to RGB if needed
        if image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
        
        # Resize if too large (for better processing)
        max_size = (800, 800)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Analyze image content
        image_description = analyze_image_content(image)
        
        # Convert to base64 for display
        image_array = np.array(image)
        image_b64 = array_to_base64(image_array)
        
        return render_template('cnn_visualizer/visualize.html',
                             original_image=image_b64,
                             image_description=image_description,
                             filename=secure_filename(file.filename))
    
    except Exception as e:
        flash(f'Error processing image: {str(e)}')
        return redirect(url_for('cnn_visualizer.index'))

@cnn_visualizer_bp.route('/visualize_block', methods=['POST'])
def visualize_block():
    """Generate CNN block visualization via AJAX"""
    try:
        data = request.get_json()
        block_number = data.get('block_number')
        image_description = data.get('image_description', 'An uploaded image')
        
        if not block_number or block_number not in [1, 2, 3, 4]:
            return jsonify({'error': 'Invalid block number'}), 400
        
        # Generate visualization description
        visualization = generate_cnn_visualization(image_description, block_number)
        
        return jsonify({
            'success': True,
            'block_number': block_number,
            'visualization': visualization
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
