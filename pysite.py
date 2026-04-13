import os
import shutil
import markdown
from pathlib import Path

# The BASE_DIR is the folder where this file exists
BASE_DIR = Path(__file__).resolve().parent
# Define the source and destination paths
LAYOUT_DIR = BASE_DIR/'layout'
PAGES_DIR = BASE_DIR/'pages'
POSTS_DIR = BASE_DIR/'posts'
OUTPUT_DIR = BASE_DIR/'docs' # use 'docs' to integrate with GitHub Pages
PUBLIC_DIR = BASE_DIR/'public'

HEAD_FILE = LAYOUT_DIR/'head.html'
HEADER_FILE = LAYOUT_DIR/'header.html'
FOOTER_FILE = LAYOUT_DIR/'footer.html'
FOOT_FILE = LAYOUT_DIR/'foot.html'

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
    if Path(OUTPUT_DIR).exists():
        shutil.rmtree(OUTPUT_DIR)
    posts_dirpath = OUTPUT_DIR/POSTS_DIR
    Path(posts_dirpath).mkdir(parents=True, exist_ok=True)
    print(f"Created clean output directory: {OUTPUT_DIR}")

def create_files_from(file_dir):
    """Combines head, header, footer and foot files with the pages or posts files to create an HTML file."""
    # Read header and footer contents
    head_content = read_file_content(HEAD_FILE)
    header_content = read_file_content(HEADER_FILE)
    footer_content = read_file_content(FOOTER_FILE)
    foot_content = read_file_content(FOOT_FILE)

    if not head_content or not foot_content:
        print("head.html or foot.html is missing content. Aborting.")
        return

    # Walk through the pages directory
    # Path.walk returns dirpath, dirnames, filenames
    for root, _, files in Path.walk(file_dir):
        for file in files:
            # Full path to the input file
            input_path = Path(root)/Path(file)
            
            # Determine relative path to preserve directory structure
            rel_path = os.path.relpath(input_path, file_dir)
            print()
            print()
            print()
            print(input_path)
            print(file_dir)
            print(rel_path)
            print()
            print()
            print()
            if file_dir == POSTS_DIR:
                output_path = os.path.join(OUTPUT_DIR, POSTS_DIR, rel_path)
            else:
                output_path = os.path.join(OUTPUT_DIR, rel_path)
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Process .html files
            if file.lower().endswith(".html"):
                # Read, modify, and write content
                with open(input_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                
                new_content = f"{head_content}\n{header_content}\n{content}\n{footer_content}\n{foot_content}"
                
                with open(output_path, "w", encoding="utf-8") as outfile:
                    outfile.write(new_content)
                
                print(f"Processed: {input_path} → {output_path}")
            # Process .md files
            elif file.lower().endswith(".md"):
                # Read, modify, and write content
                with open(input_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                
                # convert markdown to HTML
                html_content = markdown.markdown(content, extensions=["attr_list", "fenced_code", "tables", "codehilite"])
                
                new_content = f"{head_content}\n{header_content}\n<section id='md-wrap'>\n{html_content}\n</section>\n{footer_content}\n{foot_content}"

                with open(output_path, "w", encoding="utf-8") as outfile:
                    outfile.write(new_content)
                
                # Change the extension
                # Split the file path into name and extension
                base, _ = os.path.splitext(output_path)
                # Create the new file path
                new_html_file = base + ".html"
                # Rename (move) the file
                shutil.move(output_path, new_html_file)

                print(f"Processed: {input_path} (MD) → {new_html_file} (HTML)")
            else:
                # Just copy non-HTML files as-is
                with open(input_path, "rb") as src, open(output_path, "wb") as dst:
                    dst.write(src.read())
                print(f"Copied (no change): {input_path} → {output_path}")

def create_files():
    """Calls the create_files_from function to create posts and pages and copies the public folder to the OUTPUT_DIR directory"""

    # Call the create_files_from function to create the pages
    create_files_from(PAGES_DIR)

    # Call the create_files_from function to create the posts
    create_files_from(POSTS_DIR)

    # Copy CNAME file for GitHub pages with custom domain name
    if os.path.isfile("CNAME"):
        # Define destination path
        copy_file = os.path.join(OUTPUT_DIR, "CNAME")
        shutil.copy2("CNAME", copy_file)

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
