from flask import Blueprint, render_template, request, flash, redirect, url_for
import re
from collections import Counter

token_checker_bp = Blueprint('token_checker', __name__)

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
