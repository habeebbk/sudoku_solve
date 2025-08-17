from flask import Flask, render_template, request, jsonify, send_file
import os
import cv2
import numpy as np
import csv
import io
import base64
from PIL import Image
import subprocess
import tempfile
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded image temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, 'temp_sudoku.png')
        file.save(temp_path)
        
        # Run Sudoku detection
        result = run_sudoku_detection(temp_path)
        
        if result['success']:
            # Read the detected grid
            grid = read_sudoku_from_csv('sudoku_grid.csv')
            return jsonify({
                'success': True,
                'grid': grid.tolist(),
                'message': 'Sudoku detected successfully'
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/solve', methods=['POST'])
def solve_sudoku():
    try:
        data = request.get_json()
        grid = np.array(data['grid'])
        
        # Solve the Sudoku
        solution = grid.copy()
        if solve_sudoku_backtrack(solution):
            # Save solution to CSV
            save_sudoku_to_csv(solution, 'sudoku_solution.csv')
            
            # Create solution image
            solution_image = create_solution_image(solution)
            
            # Convert to base64 for display
            _, buffer = cv2.imencode('.png', solution_image)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'success': True,
                'solution': solution.tolist(),
                'image': img_base64,
                'message': 'Sudoku solved successfully'
            })
        else:
            return jsonify({'error': 'No solution found for this Sudoku puzzle'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_sudoku_detection(image_path):
    """Run Sudoku detection using the existing script"""
    try:
        # Check if sudoku_to_csv.py exists
        if not os.path.exists('sudoku_to_csv.py'):
            return {'success': False, 'error': 'Detection script not found'}
        
        # Run detection command
        cmd = [
            "python", "sudoku_to_csv.py",
            "--image", image_path,
            "--out-grid", "sudoku_grid.csv",
            "--out-cells", "sudoku_cells.csv"
        ]
        
        # Check if tesseract path exists
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tesseract_path):
            cmd.extend(["--tesseract", tesseract_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return {'success': True}
        else:
            return {'success': False, 'error': result.stderr}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def read_sudoku_from_csv(csv_file):
    """Read Sudoku puzzle from CSV file"""
    grid = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            grid.append([int(cell) for cell in row])
    return np.array(grid)

def is_valid(grid, row, col, num):
    """Check if placing 'num' at position (row, col) is valid"""
    # Check row
    for x in range(9):
        if grid[row][x] == num:
            return False
    
    # Check column
    for x in range(9):
        if grid[x][col] == num:
            return False
    
    # Check 3x3 box
    start_row = 3 * (row // 3)
    start_col = 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == num:
                return False
    
    return True

def find_empty_cell(grid):
    """Find an empty cell (cell with value 0)"""
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None

def solve_sudoku_backtrack(grid):
    """Solve the Sudoku puzzle using backtracking"""
    empty_cell = find_empty_cell(grid)
    
    if not empty_cell:
        return True
    
    row, col = empty_cell
    
    for num in range(1, 10):
        if is_valid(grid, row, col, num):
            grid[row, col] = num
            if solve_sudoku_backtrack(grid):
                return True
            grid[row, col] = 0
    
    return False

def save_sudoku_to_csv(grid, csv_file):
    """Save Sudoku grid to CSV file"""
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in grid:
            writer.writerow(row)

def create_solution_image(grid):
    """Create visual image of solved Sudoku"""
    # Image parameters
    cell_size = 60
    margin = 30
    line_thickness = 2
    
    # Calculate total image size
    total_size = 9 * cell_size + 2 * margin
    
    # Create white background
    image = np.ones((total_size, total_size, 3), dtype=np.uint8) * 255
    
    # Draw grid lines
    for i in range(10):
        x = margin + i * cell_size
        thickness = line_thickness * 2 if i % 3 == 0 else line_thickness
        cv2.line(image, (x, margin), (x, total_size - margin), (0, 0, 0), thickness)
        
        y = margin + i * cell_size
        cv2.line(image, (margin, y), (total_size - margin, y), (0, 0, 0), thickness)
    
    # Add numbers
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    font_thickness = 2
    
    for row in range(9):
        for col in range(9):
            x = margin + col * cell_size + cell_size // 2
            y = margin + row * cell_size + cell_size // 2 + 10
            
            number = grid[row][col]
            if number != 0:
                text = str(number)
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
                x = x - text_width // 2
                y = y + text_height // 2
                cv2.putText(image, text, (x, y), font, font_scale, (0, 0, 0), font_thickness)
    
    return image

if __name__ == '__main__':
    # Get port from environment variable (for production)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 