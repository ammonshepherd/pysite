import os
import shutil
import markdown
from pathlib import Path
import frontmatter

# TODO:
# - add template functionality 

# The BASE_DIR is the folder where this file exists
BASE_DIR = Path(__file__).resolve().parent
# Define the source and destination paths
LAYOUT_DIR = BASE_DIR/'layout'
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

def create_files_from_pages():
    """Take every every file in the pages folder and apply a template, then convert to HTML, if not already, and place in the appropriate path in the docs folder."""

    for item in PAGES_DIR.rglob("*"):
        relative_path = item.relative_to(PAGES_DIR)
        static_path = OUTPUT_DIR / relative_path
        # print(item)
        # print(f'relative path = {relative_path}')
        # print(f'static path = {static_path}')
        # print(type(static_path))

        # Create all sub-folders here
        if item.is_dir():
            # print(f'Make folder: {relative_path}')
            static_path.mkdir(parents=True, exist_ok=True) 

        elif item.is_file():
            # Create the path to the file
            # static_file_path = static_path.parent.mkdir(parents=True, exist_ok=True)
            # print(static_file_path)
            # print(type(static_file_path))

            # if file is an HTML file
            if item.suffix == ".html":
                # if the file has no YAML
                if frontmatter.check(item) == False:
                    # then copy as is without transformation 
                    item.copy(static_path)

                else:
                    # set the layout template
                    if 'layout' in file_contents.metadata:
                        template = file_contents['layout']
                    else:
                        template = DEFAULT_TEMPLATE
                        
                    # get contents of the template file
                    template_file = Path(f"{LAYOUT_DIR}/{template}.html")
                    template_contents = template_file.read_text()

                    # get contents of the file
                    file_contents = frontmatter.load(item)
                    
                    # replace the placeholder with the file's content
                    final_contents = template_contents.replace("{> CONTENT <}", file_contents.content)

                    # write the content to the new static file
                    static_path.write_text(final_contents)

                    # TODO: Do something with the frontmatter variables?
                        
            # if the file is a Markdown file
            elif item.suffix == '.md':
                # if the file has no YAML
                if frontmatter.check(item) == False:
                    # apply the default template
                    template = DEFAULT_TEMPLATE

                    # get contents of the template file
                    template_file = Path(f"{LAYOUT_DIR}/{template}.html")
                    template_contents = template_file.read_text()

                    # convert file contents to HTML
                    html_content = markdown.markdown(item.read_text(), extensions=["attr_list", "fenced_code", "tables", "codehilite"])

                    # replace the placeholder with file contents
                    final_contents = template_contents.replace("{> CONTENT <}", html_content)

                    # write the HTML to the new static file
                    static_path.with_suffix(".html").write_text(final_contents)

                # then process
                else:
                    # get the template
                    file_contents = frontmatter.load(item)

                    # set the layout template
                    if 'layout' in file_contents.metadata:
                        template = file_contents['layout']
                    else:
                        template = DEFAULT_TEMPLATE

                    # get contents of the template file
                    template_file = Path(f"{LAYOUT_DIR}/{template}.html")
                    template_contents = template_file.read_text()

                    html_content = markdown.markdown(file_contents.content, extensions=["attr_list", "fenced_code", "tables", "codehilite"])
                    # replace the placeholder with the file's content
                    final_contents = template_contents.replace("{> CONTENT <}", html_content)

                    # write the content to the new static file
                    static_path.with_suffix(".html").write_text(final_contents)

            # otherwise ignore the file
            else:
                continue


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
