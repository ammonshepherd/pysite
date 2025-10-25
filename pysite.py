import os
import shutil

# Define the source and destination paths
LAYOUT_DIR = 'layout'
PAGES_DIR = 'pages'
POSTS_DIR = 'posts'
OUTPUT_DIR = 'static_site'
PUBLIC_DIR = 'public'

HEAD_FILE = os.path.join(LAYOUT_DIR, 'head.html')
HEADER_FILE = os.path.join(LAYOUT_DIR, 'header.html')
FOOT_FILE = os.path.join(LAYOUT_DIR, 'foot.html')
FOOTER_FILE = os.path.join(LAYOUT_DIR, 'footer.html')

def read_file_content(filepath):
    """Reads and returns the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return ""

def create_output_directory():
    """Creates a clean output directory."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    posts_dirpath = os.path.join(OUTPUT_DIR, POSTS_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(posts_dirpath, exist_ok=True)
    print(f"Created clean output directory: {OUTPUT_DIR}")

def create_files_from(file_dir):
    """Combines head, header, body, foot and footer content to create HTML pages."""
    # Read header and footer contents
    head_content = read_file_content(HEAD_FILE)
    header_content = read_file_content(HEADER_FILE)
    footer_content = read_file_content(FOOTER_FILE)
    foot_content = read_file_content(FOOT_FILE)

    if not head_content or not foot_content:
        print("Header or footer content is missing. Aborting.")
        return

    # Walk through the pages directory
    for root, _, files in os.walk(file_dir):
        for file in files:
            # Full path to the input file
            input_path = os.path.join(root, file)
            
            # Determine relative path to preserve directory structure
            rel_path = os.path.relpath(input_path, file_dir)
            if file_dir == POSTS_DIR:
                output_path = os.path.join(OUTPUT_DIR, POSTS_DIR, rel_path)
            else:
                output_path = os.path.join(OUTPUT_DIR, rel_path)
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Process only .html files
            if file.lower().endswith(".html"):
                # Read, modify, and write content
                with open(input_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                
                new_content = f"{head_content}\n{header_content}\n{content}\n{footer_content}\n{foot_content}"
                
                with open(output_path, "w", encoding="utf-8") as outfile:
                    outfile.write(new_content)
                
                print(f"Processed: {input_path} → {output_path}")
            else:
                # Just copy non-HTML files as-is
                with open(input_path, "rb") as src, open(output_path, "wb") as dst:
                    dst.write(src.read())
                print(f"Copied (no change): {input_path} → {output_path}")

def create_files():
    """Calls the create_files_from function to create posts and pages and copies the public folder to the OUTPUT_DIR directory"""

    # Call the create_pages function to create the pages
    create_files_from(PAGES_DIR)

    # Call the create_files_from function to create the posts
    create_files_from(POSTS_DIR)

    # Copy the public directory into the static_site folder
    try:
        # This will copy the entire public folder and its contents to the new location.
        copy_path = os.path.join(OUTPUT_DIR, os.path.basename(PUBLIC_DIR))
        shutil.copytree(PUBLIC_DIR, copy_path)
        print(f"Directory '{PUBLIC_DIR}' copied successfully to '{copy_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    create_output_directory()
    create_files()
