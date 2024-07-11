import os
import subprocess

# List of folder names where your Python files are located
folder_names = ['webapp1', 'webapp2', 'webapp3, ''webapp4']  # Add your folder names here

for folder in folder_names:
    # Navigate into the folder
    os.chdir(folder)

    # Get all Python files in the current folder
    python_files = [file for file in os.listdir('.') if file.endswith('.py')]

    # Run each Python file using subprocess
    for py_file in python_files:
        subprocess.run(['python', py_file], check=True)

    # Navigate back to the parent directory
    os.chdir('..')
