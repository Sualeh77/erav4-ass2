from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
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

def get_image_generation_prompt(block_number, detailed_image_analysis):
    """Generate enhanced prompts for DALL-E image generation based on detailed image analysis"""
    
    # Extract key elements from the detailed analysis for targeted visualization
    base_context = f"Based on this detailed image analysis: {detailed_image_analysis[:500]}..."
    
    prompts = {
        1: f"""
        Create a CNN Block 1 (Edge Detection) visualization based on the uploaded image.
        
        {base_context}
        
        Transform the image to show ONLY edge detection results:
        - Convert to high-contrast black and white edge map
        - Highlight all prominent edges, contours, and boundaries mentioned in the analysis
        - Show gradients and directional changes as bright white lines
        - Remove all color and texture - focus purely on structural edges
        - Make it look like a technical Sobel or Canny edge detection output
        - Maintain the same composition and layout as the original
        
        Style: Scientific edge detection visualization, black background with bright white edges
        """,
        
        2: f"""
        Create a CNN Block 2 (Texture & Pattern Detection) visualization based on the uploaded image.
        
        {base_context}
        
        Transform the image to emphasize textures and patterns:
        - Highlight all textures, patterns, and surface details mentioned in the analysis
        - Show geometric shapes and repeated patterns with enhanced contrast
        - Convert to abstract representation focusing on texture maps
        - Emphasize curves, patterns, and material surfaces
        - Use colors that represent different texture types
        - Maintain spatial relationships from the original image
        
        Style: Abstract texture visualization with enhanced patterns and geometric emphasis
        """,
        
        3: f"""
        Create a CNN Block 3 (Object Parts Detection) visualization based on the uploaded image.
        
        {base_context}
        
        Transform the image to show object part recognition:
        - Segment and highlight distinct object components mentioned in the analysis
        - Show meaningful parts with different colors or highlighting
        - Emphasize structural elements and object components
        - Display part-based decomposition of the main objects
        - Use color coding for different object parts
        - Maintain object relationships and spatial layout
        
        Style: Segmented visualization with distinct colors for different object parts
        """,
        
        4: f"""
        Create a CNN Block 4 (Complete Object Recognition) visualization based on the uploaded image.
        
        {base_context}
        
        Transform the image to show high-level object understanding:
        - Clearly segment and label the main objects mentioned in the analysis
        - Show complete object recognition with clean boundaries
        - Simplify to essential object representations
        - Use semantic understanding to highlight complete objects
        - Display object-level classification and understanding
        - Maintain the overall composition but with simplified, recognized forms
        
        Style: Clean, simplified object recognition with clear semantic boundaries
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

def generate_cnn_image(detailed_image_analysis, block_number):
    """Generate CNN visualization image using DALL-E based on detailed image analysis"""
    if not openai_client:
        return None, "Image generation not available. Please configure OpenAI API key."
    
    try:
        prompt = get_image_generation_prompt(block_number, detailed_image_analysis)
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image and convert to base64
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            encoded_img = base64.b64encode(img_response.content).decode('utf-8')
            return f"data:image/png;base64,{encoded_img}", None
        else:
            return None, "Failed to download generated image"
            
    except Exception as e:
        return None, f"Error generating image: {str(e)}"

def analyze_image_with_gemini(image_path):
    """Analyze image content using Gemini Vision for detailed description"""
    if not client or not model:
        return "Image uploaded", "Basic image analysis not available"
    
    try:
        # Convert image to base64 for Gemini Vision
        with open(image_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        prompt = """
        Analyze this image in detail for CNN visualization purposes. Provide:
        
        1. MAIN OBJECTS: What are the primary objects/subjects in the image?
        2. VISUAL ELEMENTS: Colors, shapes, textures, patterns present
        3. COMPOSITION: Layout, positioning, background details
        4. EDGES & LINES: Prominent edges, contours, geometric elements
        5. TEXTURES: Surface textures, patterns, material appearances
        6. LIGHTING: Lighting conditions, shadows, highlights
        
        Be specific and detailed - this will be used to generate CNN layer visualizations.
        Format as a comprehensive description that captures all visual elements.
        """
        
        # Create the content with image
        content = [
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        ]
        
        response = client.models.generate_content(
            model=model,
            contents=content
        )
        
        return response.text, None
        
    except Exception as e:
        return f"Image analysis error: {str(e)}", str(e)

def analyze_image_content(image):
    """Analyze image content to provide context for CNN visualization"""
    try:
        # Try to get detailed analysis first
        detailed_analysis, error = analyze_image_with_gemini(image)
        if error:
            return "Image uploaded successfully. Click on the CNN blocks below to see how this image would transform through different layers of a Convolutional Neural Network."
        return detailed_analysis
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
        
        # Save image temporarily for Gemini Vision analysis
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            image.save(temp_file.name, format='JPEG')
            temp_path = temp_file.name
        
        # Get detailed analysis using Gemini Vision
        detailed_analysis, analysis_error = analyze_image_with_gemini(temp_path)
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        # Store detailed analysis in session for use in visualize_block
        session['detailed_image_analysis'] = detailed_analysis
        session['analysis_error'] = analysis_error
        
        # Use basic description if detailed analysis failed
        if analysis_error:
            image_description = "Image uploaded successfully. Click on the CNN blocks below to see how this image would transform through different layers of a Convolutional Neural Network."
        else:
            image_description = detailed_analysis
        
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
        generate_image = data.get('generate_image', False)
        
        if not block_number or block_number not in [1, 2, 3, 4]:
            return jsonify({'error': 'Invalid block number'}), 400
        
        # Generate text visualization description
        visualization_text = generate_cnn_visualization(image_description, block_number)
        
        result = {
            'success': True,
            'block_number': block_number,
            'visualization': visualization_text,
            'generated_image': None,
            'image_error': None
        }
        
        # Generate image if requested and OpenAI is available
        if generate_image:
            # Use detailed analysis from session if available, fallback to basic description
            detailed_analysis = session.get('detailed_image_analysis', image_description)
            generated_image, image_error = generate_cnn_image(detailed_analysis, block_number)
            result['generated_image'] = generated_image
            result['image_error'] = image_error
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
