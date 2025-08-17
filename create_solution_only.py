import cv2
import numpy as np
import csv
import os

def read_sudoku_from_csv(csv_file):
    """
    Read Sudoku solution from CSV file
    
    Args:
        csv_file: Path to the CSV file containing the solved Sudoku grid
        
    Returns:
        numpy array: 9x9 solved Sudoku grid
    """
    grid = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            grid.append([int(cell) for cell in row])
    
    return np.array(grid)

def create_sudoku_solution_image(grid):
    """
    Create a visual image of the solved Sudoku grid
    
    Args:
        grid: 9x9 solved Sudoku grid
        
    Returns:
        numpy array: Image of the solved Sudoku grid
    """
    # Image parameters
    cell_size = 80
    margin = 40
    line_thickness = 2
    
    # Calculate total image size
    total_size = 9 * cell_size + 2 * margin
    
    # Create white background
    image = np.ones((total_size, total_size, 3), dtype=np.uint8) * 255
    
    # Draw grid lines
    for i in range(10):
        # Vertical lines
        x = margin + i * cell_size
        thickness = line_thickness * 2 if i % 3 == 0 else line_thickness
        cv2.line(image, (x, margin), (x, total_size - margin), (0, 0, 0), thickness)
        
        # Horizontal lines
        y = margin + i * cell_size
        cv2.line(image, (margin, y), (total_size - margin, y), (0, 0, 0), thickness)
    
    # Add numbers
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.6
    font_thickness = 3
    
    for row in range(9):
        for col in range(9):
            # Calculate cell center
            x = margin + col * cell_size + cell_size // 2
            y = margin + row * cell_size + cell_size // 2   # Moved up 2px (was +15, now +13)
            
            # Get the number
            number = grid[row][col]
            
            if number != 0:
                # Get text size for centering
                text = str(number)
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
                
                # Adjust position for perfect centering
                x = x - text_width // 2
                y = y + text_height // 2
                
                # Draw the number
                cv2.putText(image, text, (x, y), font, font_scale, (0, 0, 0), font_thickness)
    
    # Add title at the top
    title_height = 80
    new_image = np.ones((total_size + title_height, total_size, 3), dtype=np.uint8) * 255
    
    # Copy the grid to the bottom
    new_image[title_height:, :] = image
    
    # Add title
    title = "Sudoku Solution"
    (title_width, title_height_text), baseline = cv2.getTextSize(title, font, 1.5, 3)
    title_x = (total_size - title_width) // 2
    title_y = 50
    
    cv2.putText(new_image, title, (title_x, title_y), font, 1.5, (0, 0, 0), 3)
    
    return new_image

def main():
    print("Creating Sudoku Solution Image")
    print("=" * 35)
    
    # Check if solution file exists
    solution_csv = "sudoku_solution.csv"
    
    if not os.path.exists(solution_csv):
        print(f"Error: Solution file '{solution_csv}' not found!")
        print("Please run the Sudoku solver first.")
        return
    
    try:
        # Read the solved Sudoku
        print(f"Reading solution from: {solution_csv}")
        solution_grid = read_sudoku_from_csv(solution_csv)
        
        # Create solution image
        print("Creating solution image...")
        solution_image = create_sudoku_solution_image(solution_grid)
        
        # Save the image
        filename = "sudoku_solution_image.png"
        cv2.imwrite(filename, solution_image)
        print(f"✅ Solution image saved as: {filename}")
        
        # Show image info
        height, width = solution_image.shape[:2]
        print(f"📏 Image dimensions: {width} x {height} pixels")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 