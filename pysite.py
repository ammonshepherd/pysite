import sys
import shutil
import markdown
from pathlib import Path
import frontmatter
from jinja2 import Template as yamlify

# The BASE_DIR is the folder where this file exists
BASE_DIR = Path(__file__).resolve().parent
# Define the source and destination paths
TEMPLATE_DIR = BASE_DIR/'template'
PUBLIC_DIR = BASE_DIR/'public'
PAGES_DIR = BASE_DIR/'pages'
OUTPUT_DIR = BASE_DIR/'docs' # use 'docs' to integrate with GitHub Pages
DEFAULT_TEMPLATE = 'page'
POSTS_DIR = 'posts'

# Set the base url if your site is served from a subdirectory
# ex. website.com/mysite/
# run as `python pysite.py /mysite`
BASE_URL = ''
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]
    

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

def convert_file_contents(file, prev_post, next_post):
    """Pass a file path and pass the contents through Jinja2 and Markdown parsers
       Returns the converted file contents"""
    # get contents of the file
    file_contents = frontmatter.load(file)

    # add the prev and next metadata to the file's YAML
    if prev_post is not None:
        file_contents['prev_post_url'] = f'{POSTS_DIR}/{prev_post['filename']}'
        file_contents['prev_post_title'] = prev_post['title']
    if next_post is not None:
        file_contents['next_post_url'] = f'{POSTS_DIR}/{next_post['filename']}'
        file_contents['next_post_title'] = next_post['title']

    # Add BASE_URL to YAML
    file_contents['base_url'] = BASE_URL
    # get the template or set a default
    template = file_contents.get('template', DEFAULT_TEMPLATE)
    # get contents of the template file
    template_file = Path(f"{TEMPLATE_DIR}/{template}.html")
    template_contents = template_file.read_text()
    
    # Use Jinja2 to convert all the variables in the content
    yamlified = yamlify(file_contents.content)
    converted_contents = yamlified.render(**file_contents.metadata)
    # Use Markdown parser to convert all Markdown to HTML (leaving native HTML untouched)
    htmlified = markdown.markdown(converted_contents, extensions=["attr_list", "fenced_code", "tables", "codehilite"])
    # replace the template's placeholder with the file's yamlified and htmlified content
    templated_content = template_contents.replace("{> CONTENT <}", htmlified)

    # Go over the templated content with Jinja2 again to convert the prev, next links
    final_yamilfy = yamlify(templated_content)
    return final_yamilfy.render(**file_contents.metadata)
    
def get_sorted_posts(folder_path):
    posts = []
    for file_path in Path(folder_path).glob("*"):
        post = frontmatter.load(file_path)
        post_date = post.get('date', '1900-01-01')
        post_title = post.get('title', post_date)
        posts.append({
            "filename": file_path.with_suffix(".html").name,
            "date": post_date,
            "title": post_title
        })
    posts.sort(key=lambda x: str(x['date']), reverse=False)
    return posts


def create_files_from_pages():
    """Take every every file in the pages folder and apply a template, convert to HTML, if not already, and place in the appropriate path in the docs folder."""

    posts_list = []
    if Path(PAGES_DIR/POSTS_DIR).is_dir():
        posts_list = get_sorted_posts(PAGES_DIR/POSTS_DIR)

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
                prev_post = None
                next_post = None
                if POSTS_DIR in str(static_path):
                    item_index = None
                    # Get the index # in the posts_list list of the current file
                    for i, file in enumerate(posts_list):
                        if file['filename'] == item.with_suffix(".html").name:
                            item_index = i
                            break
                    # if there is an index number, get the data from array and store in variables
                    if item_index is not None:
                        prev_post = posts_list[item_index - 1] if item_index > 0 else None
                        next_post = posts_list[item_index + 1] if item_index < len(posts_list) - 1 else None

                # pass the file through jinja2 and markdown parsers
                new_content = convert_file_contents(item, prev_post, next_post)
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

def create_post_index_page():
    posts_list = []
    if Path(PAGES_DIR/POSTS_DIR).is_dir():
        posts_list = get_sorted_posts(PAGES_DIR/POSTS_DIR)
    content = ''
    for post in posts_list:
        content += f"\n\t<a href='{BASE_URL}/{POSTS_DIR}/{post.get('filename', "")}'>{post.get('date', "")} - {post.get('title', "")}</a>"
    template_file = Path(f"{TEMPLATE_DIR}/posts-index.html")
    template_contents = template_file.read_text() 
    templated_content = template_contents.replace("{> CONTENT <}", content) 
    templated_content = templated_content.replace("{{base_url}}", BASE_URL) 
    Path(OUTPUT_DIR/POSTS_DIR/'index.html').write_text(templated_content)

if __name__ == '__main__':
    create_output_directory()
    create_files()
    create_post_index_page()
