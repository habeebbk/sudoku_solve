#!/usr/bin/env python3
"""
Simple startup script for the Sudoku Solver Web Application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'opencv-python', 'numpy', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'opencv-python':
                import cv2
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with:")
        print("   pip install -r requirements_web.txt")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = ['app.py', 'templates/index.html', 'sudoku_to_csv.py']
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🧩 Sudoku Solver Web Application")
    print("=" * 40)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found!")
    
    # Check files
    print("📁 Checking required files...")
    if not check_files():
        sys.exit(1)
    print("✅ All required files found!")
    
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("📁 Created uploads directory")
    
    print("\n🚀 Starting web application...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 