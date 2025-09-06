from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import re
from collections import Counter
import os
from dotenv import load_dotenv
import google.genai as genai

# Load environment variables
load_dotenv()

token_checker_bp = Blueprint('token_checker', __name__)

# Configure Gemini API
try:
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    model = 'gemini-2.0-flash-exp'
except Exception as e:
    print(f"Warning: Could not configure Gemini API for token checker: {e}")
    client = None
    model = None

def tokenize_text(text):
    """Tokenize text by splitting on spaces and return detailed analysis"""
    # Basic tokenization by spaces
    tokens = text.split()
    
    # Clean tokens (remove empty strings)
    tokens = [token for token in tokens if token.strip()]
    
    # Additional analysis
    unique_tokens = list(set(tokens))
    token_counts = Counter(tokens)
    
    # Calculate statistics
    total_tokens = len(tokens)
    unique_count = len(unique_tokens)
    avg_token_length = sum(len(token) for token in tokens) / total_tokens if total_tokens > 0 else 0
    
    # Character count
    total_chars = len(text)
    chars_no_spaces = len(text.replace(' ', ''))
    
    # Word frequency analysis
    most_common = token_counts.most_common(10)
    
    return {
        'tokens': tokens,
        'unique_tokens': unique_tokens,
        'token_counts': token_counts,
        'total_tokens': total_tokens,
        'unique_count': unique_count,
        'avg_token_length': avg_token_length,
        'total_chars': total_chars,
        'chars_no_spaces': chars_no_spaces,
        'most_common': most_common
    }

def advanced_tokenize(text, method='whitespace'):
    """Advanced tokenization with different methods"""
    if method == 'whitespace':
        return text.split()
    elif method == 'punctuation':
        # Split on whitespace and punctuation
        return re.findall(r'\b\w+\b', text.lower())
    elif method == 'alphanumeric':
        # Keep only alphanumeric characters
        return re.findall(r'\w+', text)
    elif method == 'words_only':
        # Only words (no numbers or special chars)
        return re.findall(r'\b[a-zA-Z]+\b', text)
    else:
        return text.split()

def get_ai_tokenization(text):
    """Get tokenization using Gemini's actual tokenizer"""
    if not client or not model:
        return None, "Gemini API not configured. Please check your API key."
    
    try:
        prompt = f"""
        You are an expert in tokenization for language models. I need you to tokenize the following text exactly as the Gemini/PaLM tokenizer would tokenize it.

        Text to tokenize: "{text}"

        Please provide:
        1. The exact tokens as they would be processed by your tokenizer
        2. The total token count
        3. Any special tokens (if present)
        4. Explanation of tokenization decisions (subword splits, punctuation handling, etc.)

        Format your response as:
        TOKENS: [list each token separated by | ]
        COUNT: [number]
        EXPLANATION: [brief explanation of how tokenization was done]

        Be precise and accurate - this is for educational purposes to understand how language models actually process text.
        """
        
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        
        return response.text, None
        
    except Exception as e:
        return None, f"Error getting AI tokenization: {str(e)}"

def parse_ai_tokenization(ai_response):
    """Parse the AI response to extract tokens and count"""
    try:
        lines = ai_response.split('\n')
        tokens = []
        count = 0
        explanation = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('TOKENS:'):
                # Extract tokens between brackets or after colon
                token_part = line.replace('TOKENS:', '').strip()
                if '[' in token_part and ']' in token_part:
                    token_part = token_part.split('[')[1].split(']')[0]
                # Split by | or comma
                if '|' in token_part:
                    tokens = [t.strip() for t in token_part.split('|') if t.strip()]
                else:
                    tokens = [t.strip() for t in token_part.split(',') if t.strip()]
            elif line.startswith('COUNT:'):
                count_str = line.replace('COUNT:', '').strip()
                try:
                    count = int(count_str)
                except:
                    count = len(tokens)
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
        
        # Fallback: if no count found, use token list length
        if count == 0:
            count = len(tokens)
            
        return {
            'tokens': tokens,
            'count': count,
            'explanation': explanation,
            'raw_response': ai_response
        }
        
    except Exception as e:
        return {
            'tokens': [],
            'count': 0,
            'explanation': f"Error parsing response: {str(e)}",
            'raw_response': ai_response
        }

@token_checker_bp.route('/')
def index():
    return render_template('token_checker/index.html')

@token_checker_bp.route('/analyze', methods=['POST'])
def analyze_text():
    text = request.form.get('text', '').strip()
    method = request.form.get('method', 'whitespace')
    
    if not text:
        flash('Please enter some text to analyze.')
        return redirect(url_for('token_checker.index'))
    
    try:
        # Perform basic analysis
        basic_analysis = tokenize_text(text)
        
        # Perform advanced tokenization based on selected method
        advanced_tokens = advanced_tokenize(text, method)
        advanced_token_count = len(advanced_tokens)
        advanced_unique_count = len(set(advanced_tokens))
        
        return render_template('token_checker/result.html',
                             text=text,
                             method=method,
                             basic_analysis=basic_analysis,
                             advanced_tokens=advanced_tokens,
                             advanced_token_count=advanced_token_count,
                             advanced_unique_count=advanced_unique_count)
    
    except Exception as e:
        flash(f'Error analyzing text: {str(e)}')
        return redirect(url_for('token_checker.index'))

@token_checker_bp.route('/ai_tokenize', methods=['POST'])
def ai_tokenize():
    """Get AI-powered tokenization via AJAX"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 2000:  # Limit text length
            return jsonify({'error': 'Text too long. Please limit to 2000 characters.'}), 400
        
        # Get AI tokenization
        ai_response, error = get_ai_tokenization(text)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Parse the response
        parsed_result = parse_ai_tokenization(ai_response)
        
        return jsonify({
            'success': True,
            'ai_tokens': parsed_result['tokens'],
            'ai_count': parsed_result['count'],
            'explanation': parsed_result['explanation'],
            'raw_response': parsed_result['raw_response']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
