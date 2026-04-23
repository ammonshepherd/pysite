import os
import shutil
import markdown
from pathlib import Path
import frontmatter
from jinja2 import Template as yamlify

# TODO:
# - add template functionality 

# The BASE_DIR is the folder where this file exists
BASE_DIR = Path(__file__).resolve().parent
# Define the source and destination paths
TEMPLATE_DIR = BASE_DIR/'template'
PAGES_DIR = BASE_DIR/'pages'
PUBLIC_DIR = BASE_DIR/'public'
OUTPUT_DIR = BASE_DIR/'docs' # use 'docs' to integrate with GitHub Pages
DEFAULT_TEMPLATE = 'page'

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
    except Exception as e:
        print(f"Error creating output directory {OUTPUT_DIR}: \n{e}")
        return 

def convert_file_contents(file):
    """Pass a file path and pass the contents through Jinja2 and Markdown parsers
       Returns the converted file contents"""
    # get contents of the file
    file_contents = frontmatter.load(file)
    # get the template or set a default
    template = file_contents.get('template', DEFAULT_TEMPLATE)
    # get contents of the template file
    template_file = Path(f"{TEMPLATE_DIR}/{template}.html")
    template_contents = template_file.read_text()
    # Use Jinja2 to convert all the variables in the content
    yamlified = yamlify(file_contents.content)
    converted_contents = yamlified.render(**file_contents.metadata)
    file_contents.content = converted_contents
    # Use Markdown parser to convert all Markdown to HTML (leaving native HTML untouched)
    htmlified = markdown.markdown(file_contents.content, extensions=["attr_list", "fenced_code", "tables", "codehilite"])
    # replace the template's placeholder with the file's yamlified and htmlified content
    final_contents = template_contents.replace("{> CONTENT <}", htmlified)
    return final_contents
    
def create_files_from_pages():
    """Take every every file in the pages folder and apply a template, convert to HTML, if not already, and place in the appropriate path in the docs folder."""

    for item in PAGES_DIR.rglob("*"):
        # Create the static path for the file/folder
        static_path = OUTPUT_DIR / item.relative_to(PAGES_DIR)
        # Create folders
        if item.is_dir():
            static_path.mkdir(parents=True, exist_ok=True) 
        # Create files
        elif item.is_file():
            # if file is an HTML file and has no YAML
            if item.suffix == ".html" and frontmatter.check(item) == False:
                # then copy as is without transformation 
                item.copy(static_path)
            else:
                # pass the file through jinja2 and markdown parsers
                new_content = convert_file_contents(item)
                # write the new static file
                static_path.with_suffix(".html").write_text(new_content)

def create_files():
    """Calls the create_files_from_pages function, and copies the public folder and the CNAME file if it exists to the output folder"""

    # Call the create_files_from function to create the pages
    create_files_from_pages()

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
