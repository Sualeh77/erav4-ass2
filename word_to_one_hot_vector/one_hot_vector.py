from flask import Blueprint, render_template, request, flash, redirect, url_for
import numpy as np
import json

one_hot_vector_bp = Blueprint('one_hot_vector', __name__)

def create_vocabulary(words):
    """Create vocabulary from list of words"""
    # Remove duplicates and sort for consistency
    unique_words = sorted(list(set(word.lower().strip() for word in words if word.strip())))
    vocab = {word: idx for idx, word in enumerate(unique_words)}
    return vocab, unique_words

def word_to_one_hot(word, vocab):
    """Convert a word to one-hot vector"""
    word = word.lower().strip()
    if word not in vocab:
        return None
    
    vector = np.zeros(len(vocab))
    vector[vocab[word]] = 1
    return vector

def words_to_one_hot_matrix(words, vocab):
    """Convert list of words to one-hot matrix"""
    matrix = []
    valid_words = []
    
    for word in words:
        word = word.lower().strip()
        if word in vocab:
            vector = word_to_one_hot(word, vocab)
            matrix.append(vector)
            valid_words.append(word)
    
    return np.array(matrix), valid_words

@one_hot_vector_bp.route('/')
def index():
    return render_template('one_hot_vector/index.html')

@one_hot_vector_bp.route('/process', methods=['POST'])
def process_words():
    words_input = request.form.get('words', '').strip()
    selected_word = request.form.get('selected_word', '').strip().lower()
    
    if not words_input:
        flash('Please enter some words.')
        return redirect(url_for('one_hot_vector.index'))
    
    try:
        # Parse words (split by commas, newlines, or spaces)
        import re
        words = re.split(r'[,\n\s]+', words_input)
        words = [word.strip() for word in words if word.strip()]
        
        if len(words) < 2:
            flash('Please enter at least 2 words.')
            return redirect(url_for('one_hot_vector.index'))
        
        # Create vocabulary
        vocab, unique_words = create_vocabulary(words)
        vocab_size = len(vocab)
        
        # Create one-hot vectors for all words
        one_hot_matrix, valid_words = words_to_one_hot_matrix(words, vocab)
        
        # Handle selected word
        selected_vector = None
        selected_index = None
        if selected_word and selected_word in vocab:
            selected_vector = word_to_one_hot(selected_word, vocab)
            selected_index = vocab[selected_word]
        elif selected_word:
            flash(f'Selected word "{selected_word}" not found in vocabulary.')
        
        # Prepare data for template
        vocab_list = [(word, idx) for word, idx in sorted(vocab.items(), key=lambda x: x[1])]
        
        # Create word-vector pairs for display
        word_vectors = []
        for i, word in enumerate(valid_words):
            vector = one_hot_matrix[i]
            word_vectors.append({
                'word': word,
                'vector': vector.tolist(),
                'index': vocab[word]
            })
        
        return render_template('one_hot_vector/result.html',
                             words=words,
                             unique_words=unique_words,
                             vocab=vocab_list,
                             vocab_size=vocab_size,
                             word_vectors=word_vectors,
                             selected_word=selected_word,
                             selected_vector=selected_vector.tolist() if selected_vector is not None else None,
                             selected_index=selected_index,
                             one_hot_matrix=one_hot_matrix.tolist())
    
    except Exception as e:
        flash(f'Error processing words: {str(e)}')
        return redirect(url_for('one_hot_vector.index'))
