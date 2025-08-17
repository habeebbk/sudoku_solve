# 🧩 Sudoku Solver Web Application

A modern, responsive web application that uses AI-powered image recognition to detect and solve Sudoku puzzles from photos.

## ✨ Features

- **📸 Image Upload**: Drag & drop or click to upload Sudoku images
- **🔍 AI Detection**: Advanced OCR technology to recognize Sudoku grids
- **🧠 Smart Solving**: Powerful backtracking algorithm to solve any valid puzzle
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **💾 Export Results**: Download solution images and CSV files
- **🎨 Modern UI**: Beautiful gradient design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR installed (optional, for better accuracy)

### Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements_web.txt
   ```

3. **Install Tesseract OCR (Optional but recommended):**
   - **Windows**: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## 🎯 How to Use

1. **Upload Image**: Drag and drop a Sudoku image or click to browse
2. **Click "Detect & Solve"**: The app will automatically detect the grid and solve the puzzle
3. **View Results**: See both the original puzzle and the solution
4. **Download**: Save the solution image to your device

## 🏗️ Architecture

### Backend (Flask)
- **`app.py`**: Main Flask application with API endpoints
- **Image Processing**: Uses OpenCV and PIL for image handling
- **Sudoku Detection**: Integrates with existing `sudoku_to_csv.py` script
- **Solving Algorithm**: Implements backtracking algorithm for puzzle solving

### Frontend (HTML/CSS/JavaScript)
- **Modern Design**: Gradient backgrounds and card-based layout
- **Responsive Grid**: CSS Grid for adaptive layouts
- **Interactive Elements**: Drag & drop, loading animations, status messages
- **Real-time Updates**: AJAX calls for seamless user experience

## 📁 File Structure

```
sudoku_solver_web/
├── app.py                 # Flask backend application
├── templates/
│   └── index.html        # Main HTML template
├── requirements_web.txt   # Python dependencies
├── README_WEB.md         # This file
├── sudoku_to_csv.py      # Existing detection script
└── uploads/              # Temporary upload folder (auto-created)
```

## 🔧 API Endpoints

### POST `/upload`
- **Purpose**: Upload and detect Sudoku image
- **Input**: Multipart form data with image file
- **Output**: JSON with detected grid data

### POST `/solve`
- **Purpose**: Solve Sudoku puzzle
- **Input**: JSON with grid data
- **Output**: JSON with solution and image

## 🎨 Customization

### Colors and Themes
Edit the CSS variables in `templates/index.html`:
```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --accent-color: #4facfe;
}
```

### Grid Styling
Modify the `.grid-cell` CSS class to change:
- Cell size and spacing
- Border styles and colors
- Font sizes and colors

### Animation Effects
Adjust transition timings in CSS:
```css
transition: all 0.3s ease;
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=0
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **For Docker deployment:**
   ```dockerfile
   FROM python:3.9-slim
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements_web.txt
   EXPOSE 5000
   CMD ["python", "app.py"]
   ```

## 🔍 Troubleshooting

### Common Issues

1. **"Detection script not found"**
   - Ensure `sudoku_to_csv.py` is in the same directory as `app.py`

2. **OCR errors**
   - Install Tesseract OCR or check the path in `app.py`

3. **Image upload fails**
   - Check file size (max 16MB)
   - Ensure image format is supported (PNG, JPG, JPEG, BMP, TIFF)

4. **Port already in use**
   - Change port in `app.py`: `app.run(port=5001)`

### Performance Tips

- Use smaller images for faster processing
- Ensure Tesseract OCR is installed for better accuracy
- Monitor server resources during heavy usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- OpenCV for image processing
- Tesseract for OCR capabilities
- Flask for the web framework
- Font Awesome for icons

---

**Happy Sudoku Solving! 🎉** 