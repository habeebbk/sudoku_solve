import csv
import numpy as np
import os

def read_sudoku_from_csv(csv_file):
    """
    Read Sudoku puzzle from CSV file
    
    Args:
        csv_file: Path to the CSV file containing the Sudoku grid
        
    Returns:
        numpy array: 9x9 Sudoku grid (0 for empty cells)
    """
    grid = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            grid.append([int(cell) for cell in row])
    
    return np.array(grid)

def is_valid(grid, row, col, num):
    """
    Check if placing 'num' at position (row, col) is valid
    
    Args:
        grid: Current Sudoku grid
        row: Row index
        col: Column index
        num: Number to place
        
    Returns:
        bool: True if placement is valid, False otherwise
    """
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
    """
    Find an empty cell (cell with value 0)
    
    Args:
        grid: Current Sudoku grid
        
    Returns:
        tuple: (row, col) of empty cell, or None if no empty cells
    """
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None

def solve_sudoku(grid):
    """
    Solve the Sudoku puzzle using backtracking
    
    Args:
        grid: 9x9 Sudoku grid
        
    Returns:
        bool: True if solution found, False otherwise
    """
    empty_cell = find_empty_cell(grid)
    
    # If no empty cell, puzzle is solved
    if not empty_cell:
        return True
    
    row, col = empty_cell
    
    # Try numbers 1-9
    for num in range(1, 10):
        if is_valid(grid, row, col, num):
            # Place the number
            grid[row][col] = num
            
            # Recursively try to solve the rest
            if solve_sudoku(grid):
                return True
            
            # If placing num didn't lead to a solution, backtrack
            grid[row][col] = 0
    
    # No solution found with this number
    return False

def save_sudoku_to_csv(grid, csv_file):
    """
    Save Sudoku grid to CSV file
    
    Args:
        grid: 9x9 Sudoku grid
        csv_file: Path to output CSV file
    """
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in grid:
            writer.writerow(row)

def print_sudoku_grid(grid, title="Sudoku Grid"):
    """
    Print Sudoku grid in a nice format
    
    Args:
        grid: 9x9 Sudoku grid
        title: Title for the grid
    """
    print(f"\n{title}")
    print("=" * 50)
    
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        
        row_str = ""
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row_str += "| "
            
            if grid[i][j] == 0:
                row_str += ". "
            else:
                row_str += f"{grid[i][j]} "
        
        print(row_str)
    
    print("=" * 50)

def main():
    print("Sudoku Solver")
    print("=" * 30)
    
    # Input CSV file (the one we just created)
    input_csv = "sudoku_grid.csv"
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found!")
        print("Please make sure you have run the Sudoku detector first.")
        return
    
    try:
        # Read the Sudoku puzzle
        print(f"Reading Sudoku puzzle from: {input_csv}")
        puzzle = read_sudoku_from_csv(input_csv)
        
        # Display the original puzzle
        print_sudoku_grid(puzzle, "Original Puzzle")
        
        # Create a copy for solving
        solution = puzzle.copy()
        
        # Solve the puzzle
        print("\nSolving Sudoku puzzle...")
        if solve_sudoku(solution):
            print("✅ Sudoku solved successfully!")
            
            # Display the solution
            print_sudoku_grid(solution, "Solution")
            
            # Save the solution to a new CSV file
            output_csv = "sudoku_solution.csv"
            save_sudoku_to_csv(solution, output_csv)
            print(f"\n💾 Solution saved to: {output_csv}")
            
            # Also save a comparison file showing original vs solution
            comparison_csv = "sudoku_comparison.csv"
            with open(comparison_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["row", "col", "original", "solution"])
                for i in range(9):
                    for j in range(9):
                        writer.writerow([i, j, puzzle[i][j], solution[i][j]])
            
            print(f"📊 Comparison saved to: {comparison_csv}")
            
        else:
            print("❌ No solution found for this Sudoku puzzle!")
            print("The puzzle might be unsolvable or have invalid initial values.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
