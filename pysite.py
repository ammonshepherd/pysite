import os
import shutil
import markdown
from pathlib import Path

# TODO:
# - add a layout/page.py and layout/post.py template

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
        print(f"WARNING: {filepath} not found.")
        return ""

def create_output_directory():
    """Creates a clean output directory."""
    try:
        if OUTPUT_DIR.exists() and OUTPUT_DIR.is_dir:
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created clean output directory: {OUTPUT_DIR}")
    except:
        print(f"Error creating output directory {OUTPUT_DIR}")
        return 

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

    # Create the output directory
    try:
        # if it's the pages directory, then don't create a subdirectory of docs
        if file_dir.name == 'pages':
            output_dir = OUTPUT_DIR
        else:
            output_dir = OUTPUT_DIR/file_dir.name
            output_dir.mkdir(exist_ok=True)
            print(f"Successfully created {output_dir} directory.")
    except:
        print(f"Error: Could not create {output_dir}.")
    
    # Path.walk returns dirpath, dirnames, filenames
    for root, _, files in Path.walk(file_dir):
        for file in files:
            # Full path to the input file
            input_path = file_dir/file
            # Determine relative path to preserve directory structure
            rel_path = input_path.name
            output_path = output_dir/rel_path

            # Process .html files
            if file.lower().endswith(".html"):
                # Read, modify, and write content
                with open(input_path, "r", encoding="utf-8") as in_file:
                    content = in_file.read()
                
                new_content = f"{head_content}\n{header_content}\n{content}\n{footer_content}\n{foot_content}"
                
                with open(output_path, "w", encoding="utf-8") as outfile:
                    outfile.write(new_content)
                
                print(f"Processed: {input_path} → {output_path}")
            # Process .md files
            elif file.lower().endswith(".md"):
                # Read, modify, and write content
                with open(input_path, "r", encoding="utf-8") as in_file:
                    content = in_file.read()
                
                # convert markdown to HTML
                html_content = markdown.markdown(content, extensions=["attr_list", "fenced_code", "tables", "codehilite"])
                
                new_content = f"{head_content}\n{header_content}\n<section id='md-wrap'>\n{html_content}\n</section>\n{footer_content}\n{foot_content}"

                with open(output_path, "w", encoding="utf-8") as outfile:
                    outfile.write(new_content)
                
                # Change the extension
                new_out_path = output_path.rename(output_path.with_suffix(".html"))

                print(f"Processed: {input_path} (MD) → {new_out_path} (HTML)")
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
    if Path("CNAME").is_file():
        Path("CNAME").copy(OUTPUT_DIR/"CNAME")

    # Copy the public directory into the static_site folder
    try:
        # This will copy the entire public folder and its contents to the new location.
        PUBLIC_DIR.copy(OUTPUT_DIR/PUBLIC_DIR.name)
        print(f"Directory '{PUBLIC_DIR}' copied successfully to '{OUTPUT_DIR/PUBLIC_DIR.name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    create_output_directory()
    create_files()
