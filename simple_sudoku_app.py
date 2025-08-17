import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import csv
import numpy as np
import cv2
from PIL import Image, ImageTk

class SimpleSudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Sudoku Image Processor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.image_path = None
        self.original_grid = None
        self.solution_grid = None
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Simple Sudoku Image Processor", 
                             font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, bg='#f0f0f0', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        
        # Upload section
        upload_frame = tk.LabelFrame(left_panel, text="Upload Image", bg='#f0f0f0', 
                                   font=("Arial", 12, "bold"))
        upload_frame.pack(fill='x', pady=(0, 20))
        
        self.upload_btn = tk.Button(upload_frame, text="Choose Image", 
                                   command=self.upload_image, 
                                   bg='#4CAF50', fg='white', font=("Arial", 10),
                                   relief='flat', padx=20, pady=10)
        self.upload_btn.pack(pady=10)
        
        self.image_label = tk.Label(upload_frame, text="No image selected", 
                                  bg='#f0f0f0', fg='#666666')
        self.image_label.pack(pady=5)
        
        # Process section
        process_frame = tk.LabelFrame(left_panel, text="Process Image", bg='#f0f0f0',
                                    font=("Arial", 12, "bold"))
        process_frame.pack(fill='x', pady=(0, 20))
        
        self.solve_btn = tk.Button(process_frame, text="Solve Sudoku", 
                                 command=self.solve_and_save_sudoku, 
                                 bg='#FF9800', fg='white', font=("Arial", 10),
                                 relief='flat', padx=20, pady=10, state='disabled')
        self.solve_btn.pack(pady=10)
        
        # Status section
        status_frame = tk.LabelFrame(left_panel, text="Status", bg='#f0f0f0',
                                   font=("Arial", 12, "bold"))
        status_frame.pack(fill='x')
        
        self.status_text = tk.Text(status_frame, height=15, width=35, 
                                 font=("Consolas", 10), bg='#f8f8f8')
        self.status_text.pack(padx=10, pady=10, fill='both')
        
        # Right panel - Display (split into two sections)
        right_panel = tk.Frame(main_frame, bg='#f0f0f0')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Top display frame - Original Image
        original_frame = tk.LabelFrame(right_panel, text="Original Image", bg='#f0f0f0',
                                     font=("Arial", 12, "bold"))
        original_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.original_label = tk.Label(original_frame, text="Upload an image to start", 
                                     bg='#f8f8f8', fg='#666666', font=("Arial", 14))
        self.original_label.pack(expand=True, fill='both')
        
        # Bottom display frame - Solution Image
        solution_frame = tk.LabelFrame(right_panel, text="Solution Image", bg='#f0f0f0',
                                     font=("Arial", 12, "bold"))
        solution_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.solution_label = tk.Label(solution_frame, text="Solve Sudoku to see solution", 
                                     bg='#f8f8f8', fg='#666666', font=("Arial", 14))
        self.solution_label.pack(expand=True, fill='both')
        

        
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Choose Sudoku Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=os.path.basename(file_path))
            self.solve_btn.config(state='normal')
            self.display_original_image(file_path)
            self.log_status(f"Image uploaded: {os.path.basename(file_path)}")
            
    def display_original_image(self, image_path):
        try:
            # Load and resize image for display
            image = Image.open(image_path)
            
            # Resize for display
            max_size = 250
            width, height = image.size
            if max(width, height) > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update display
            self.original_label.config(image=photo, text="")
            self.original_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.log_status(f"Error displaying image: {str(e)}")
    
    def display_solution_image(self, grid):
        try:
            # Create solution image using existing create_solution_image function
            solution_image = self.create_solution_image(grid)
            
            # Convert numpy array to PIL Image
            solution_image_rgb = cv2.cvtColor(solution_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(solution_image_rgb)
            
            # Resize for display
            max_size = 250
            width, height = pil_image.size
            if max(width, height) > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update display
            self.solution_label.config(image=photo, text="")
            self.solution_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.log_status(f"Error displaying solution image: {str(e)}")
            
    def read_sudoku_from_csv(self, csv_file):
        """Read Sudoku puzzle from CSV file"""
        grid = []
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                grid.append([int(cell) for cell in row])
        return np.array(grid)
    
    def is_valid(self, grid, row, col, num):
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
    
    def find_empty_cell(self, grid):
        """Find an empty cell (cell with value 0)"""
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return (i, j)
        return None
    
    def solve_sudoku_backtrack(self, grid):
        """Solve the Sudoku puzzle using backtracking"""
        empty_cell = self.find_empty_cell(grid)
        
        if not empty_cell:
            return True
        
        row, col = empty_cell
        
        for num in range(1, 10):
            if self.is_valid(grid, row, col, num):
                grid[row, col] = num
                if self.solve_sudoku_backtrack(grid):
                    return True
                grid[row, col] = 0
        
        return False
    
    def save_sudoku_to_csv(self, grid, csv_file):
        """Save Sudoku grid to CSV file"""
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in grid:
                writer.writerow(row)
    
    def solve_and_save_sudoku(self):
        """Automatically detect and solve the uploaded Sudoku puzzle"""
        if not self.image_path:
            messagebox.showerror("Error", "Please upload an image first!")
            return
        
        try:
            # Step 1: Run Sudoku detection automatically
            self.log_status("Starting automatic Sudoku detection...")
            self.log_status(f"Processing: {os.path.basename(self.image_path)}")
            
            # Run sudoku_to_csv.py with the uploaded image
            cmd = [
                "python", "sudoku_to_csv.py",
                "--image", self.image_path,
                "--out-grid", "sudoku_grid.csv",
                "--out-cells", "sudoku_cells.csv"
            ]
            
            # Check if tesseract path exists and add it if available
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                cmd.extend(["--tesseract", tesseract_path])
                self.log_status("Using Tesseract OCR for digit recognition")
            else:
                self.log_status("Tesseract not found, using basic detection")
            
            self.log_status("Running detection command...")
            
            # Run the detection command
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                self.log_status(f"❌ Error during detection:")
                self.log_status(result.stderr)
                messagebox.showerror("Error", "Sudoku detection failed!\nCheck the status log for details.")
                return
            
            self.log_status("✅ Sudoku detection completed successfully!")
            self.log_status("Files created:")
            self.log_status("  - sudoku_grid.csv")
            self.log_status("  - sudoku_cells.csv")
            
            # Step 2: Read and solve the puzzle
            self.log_status("Reading Sudoku puzzle from CSV...")
            self.original_grid = self.read_sudoku_from_csv("sudoku_grid.csv")
            
            self.log_status("Solving Sudoku puzzle...")
            solution = self.original_grid.copy()
            
            if self.solve_sudoku_backtrack(solution):
                self.solution_grid = solution
                self.log_status("✅ Sudoku solved successfully!")
                
                # Save solution to CSV
                self.save_sudoku_to_csv(solution, "sudoku_solution.csv")
                self.log_status("💾 Solution saved to: sudoku_solution.csv")
                
                # Save comparison file
                with open("sudoku_comparison.csv", 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["row", "col", "original", "solution"])
                    for i in range(9):
                        for j in range(9):
                            writer.writerow([i, j, self.original_grid[i][j], solution[i][j]])
                
                self.log_status("📊 Comparison saved to: sudoku_comparison.csv")
                
                # Display solution image
                self.display_solution_image(solution)
                self.log_status("🖼️ Solution image displayed!")
                
                messagebox.showinfo("Success", "Sudoku solved successfully!")
                
            else:
                self.log_status("❌ No solution found for this Sudoku puzzle!")
                messagebox.showerror("Error", "No solution found for this Sudoku puzzle!")
                
        except Exception as e:
            self.log_status(f"❌ Error solving Sudoku: {str(e)}")
            messagebox.showerror("Error", f"Failed to solve Sudoku: {str(e)}")
    
    def create_solution_image(self, grid):
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
    
    def log_status(self, message):
        """Add message to status log"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)

def main():
    root = tk.Tk()
    app = SimpleSudokuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 