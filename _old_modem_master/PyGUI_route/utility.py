import os

def create_directory(filename):
    # Extract the directory name from the file path
    dirname = os.path.dirname(filename)
    
    # Create the directory if it does not exist
    if not os.path.exists(dirname):
        os.makedirs(dirname)
