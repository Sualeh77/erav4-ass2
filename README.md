# AI Tools Dashboard 🚀

A comprehensive Flask-based web application featuring multiple AI and image processing tools. Built with modern UI/UX and organized into modular components.

## 🛠️ Tools Included

### 1. **Image Filter** 🖼️
- **Location**: `image_filter_demo/`
- **Features**: 
  - Custom 3x3 convolution kernel input
  - Real-time image filtering
  - Preset filters (Edge Detection, Blur, Sharpen, Emboss)
  - Before/after comparison view
  - Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP)

### 2. **Image Normalizer** 📊
- **Location**: `image_normalizer/`
- **Features**:
  - Mean normalization calculation and application
  - Statistical analysis (mean, std, min, max for each channel)
  - RGB and Grayscale support
  - Visual comparison of original vs normalized images
  - Detailed channel-wise statistics

### 3. **Token Length Checker** 📝
- **Location**: `token_length_checker/`
- **Features**:
  - Multiple tokenization methods (whitespace, punctuation removal, etc.)
  - Comprehensive text statistics
  - Token frequency analysis
  - Character and word count analysis
  - Sample text templates

### 4. **Word to One-Hot Vector** 🔢
- **Location**: `word_to_one_hot_vector/`
- **Features**:
  - One-hot encoding for word lists
  - Vocabulary management
  - Interactive vector visualization
  - Matrix view of all vectors
  - Highlight selected words
  - Sample word categories (animals, colors, fruits)

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- UV package manager (recommended) or pip

### Installation & Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd s2_assignment
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```
   *Or with pip:*
   ```bash
   pip install flask pillow numpy werkzeug
   ```

3. **Start the application**:
   ```bash
   ./start.sh
   ```
   *Or manually:*
   ```bash
   source .venv/bin/activate
   python run.py
   ```

4. **Access the dashboard**:
   Open your browser and go to: `http://localhost:5000`

## 📁 Project Structure

```
s2_assignment/
├── main.py                 # Main Flask application
├── run.py                  # Application runner with nice output
├── start.sh               # Quick start script
├── pyproject.toml         # Project dependencies
├── templates/             # HTML templates
│   ├── base.html          # Base template with styling
│   ├── index.html         # Main dashboard
│   ├── image_filter/      # Image filter templates
│   ├── image_normalizer/  # Image normalizer templates
│   ├── token_checker/     # Token checker templates
│   └── one_hot_vector/    # One-hot vector templates
├── image_filter_demo/     # Image filtering tool
├── image_normalizer/      # Image normalization tool
├── token_length_checker/  # Text tokenization tool
└── word_to_one_hot_vector/ # One-hot encoding tool
```

## 🎨 Features

### Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Bootstrap 5**: Modern styling and components
- **Gradient Themes**: Each tool has its unique color scheme
- **Interactive Elements**: Hover effects and smooth transitions
- **Font Awesome Icons**: Professional iconography

### Technical Features
- **Modular Architecture**: Each tool is a separate Flask Blueprint
- **Error Handling**: Comprehensive error handling and user feedback
- **File Upload**: Secure file handling with size limits
- **Real-time Processing**: Immediate results without page refresh
- **Sample Data**: Built-in examples for quick testing

## 🔧 Tool Details

### Image Filter
**Algorithm**: 2D Convolution
- Input: 3x3 numeric kernel + image
- Process: Convolution operation with edge padding
- Output: Filtered image with before/after comparison

### Image Normalizer  
**Algorithm**: Mean Normalization
- Formula: `normalized = (pixel - mean) rescaled to [0,255]`
- Supports both RGB and Grayscale images
- Provides detailed statistical analysis

### Token Length Checker
**Methods**:
- Whitespace tokenization (split by spaces)
- Punctuation removal
- Alphanumeric only
- Words only (no numbers)

### One-Hot Vector
**Process**:
1. Create vocabulary from input words
2. Assign unique index to each word
3. Generate binary vectors (length = vocab size)
4. Display in multiple formats (table, matrix, highlighted)

## 🚀 Usage Examples

### Image Filter
1. Upload an image (PNG, JPG, etc.)
2. Set a 3x3 kernel (try presets or custom values)
3. Click "Apply Filter" to see results
4. Compare original vs filtered images

### Image Normalizer
1. Upload any image
2. Click "Calculate Mean & Normalize"
3. View statistical analysis and normalized result
4. Compare before/after images

### Token Checker
1. Enter text in the textarea
2. Choose tokenization method
3. Click "Analyze Tokens"
4. Review detailed statistics and token lists

### One-Hot Vector
1. Enter 10+ words (comma or space separated)
2. Optionally select a word to highlight
3. Click "Generate One-Hot Vectors"
4. Explore vocabulary, vectors, and matrix view

## 🛡️ Security & Limits

- **File Size**: Maximum 16MB per upload
- **File Types**: Only image files allowed for image tools
- **Temporary Storage**: Uploaded files are processed in memory
- **Input Validation**: All inputs are validated and sanitized

## 🔧 Development

### Adding New Tools
1. Create new directory: `new_tool/`
2. Add `__init__.py` and `new_tool.py`
3. Create Blueprint with routes
4. Add templates in `templates/new_tool/`
5. Register Blueprint in `main.py`
6. Add navigation link in `index.html`

### Customization
- **Styling**: Modify `templates/base.html` for global styles
- **Colors**: Update gradient CSS in individual templates
- **Features**: Each tool is independent and easily extensible

## 📚 Dependencies

- **Flask 3.0+**: Web framework
- **Pillow 10.0+**: Image processing
- **NumPy 1.24+**: Numerical computations
- **Werkzeug 3.0+**: File handling utilities

## 🏃‍♂️ Quick Commands

```bash
# Start application
./start.sh

# Install dependencies
uv sync

# Run with manual activation
source .venv/bin/activate && python run.py

# Check imports
source .venv/bin/activate && python -c "import main; print('OK')"
```

## 💡 Tips

1. **Image Filter**: Try edge detection kernel `[-1,-1,-1,-1,8,-1,-1,-1,-1]`
2. **Token Checker**: Use sample texts for quick testing
3. **One-Hot Vector**: Try the animal/color/fruit presets
4. **Image Normalizer**: Works best with natural photos

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies**
