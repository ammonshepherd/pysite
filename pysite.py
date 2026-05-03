import sys
import shutil
import markdown
from pathlib import Path
import frontmatter
from jinja2 import Environment, FileSystemLoader

# --- CONFIGURATION & SETTINGS ---

# The BASE_DIR is the folder where this file exists
BASE_DIR = Path(__file__).resolve().parent

# Define defaults first
config = {
    "template_dir": 'template',
    "public_dir": 'public',
    "pages_dir": 'pages',
    "output_dir": 'docs',
    "default_template": 'page',
    "posts_dir": 'posts',
    "post_index_template": 'posts-index.html',
    "base_url": ''
}
# Update settings if file exists
settings_path = Path('settings.yml')
if settings_path.exists():
    settings_file = frontmatter.load('settings.yml')
    config.update(settings_file.metadata)

# Path Assignments
TEMPLATE_DIR = BASE_DIR / config["template_dir"]
PUBLIC_DIR = BASE_DIR / config["public_dir"]
PAGES_DIR = BASE_DIR / config["pages_dir"]
OUTPUT_DIR = BASE_DIR / config["output_dir"]
DEFAULT_TEMPLATE = config["default_template"]
POSTS_DIR = config["posts_dir"]
POST_INDEX_TEMPLATE = config["post_index_template"]
BASE_URL = ""

if len(sys.argv) > 1:
    BASE_URL = settings_file.get("base_url", '') # CHANGE to the subdirectory of your site

template_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# --- HELPER FUNCTIONS ---

def get_sorted_posts():
    """Retrieves and sorts posts from the specific posts directory."""
    posts_path = PAGES_DIR / POSTS_DIR
    if not posts_path.is_dir():
        return []

    posts = []
    for file_path in posts_path.glob("*"):
        if file_path.is_file():
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

def convert_file_contents(file, prev_post=None, next_post=None):
    """Processes Markdown/Jinja content into final HTML.
       Pass a file path and pass the contents through Jinja2 
       and Markdown parsers Returns the converted file contents"""
    # get contents of the file
    page = frontmatter.load(file)
    # Add BASE_URL to YAML
    page['base_url'] = BASE_URL

    # add the prev and next metadata to the file's YAML
    if prev_post is not None:
        page['prev_post_url'] = f'{POSTS_DIR}/{prev_post['filename']}'
        page['prev_post_title'] = prev_post['title']
    if next_post is not None:
        page['next_post_url'] = f'{POSTS_DIR}/{next_post['filename']}'
        page['next_post_title'] = next_post['title']

    # Create the content using the template's content and the file's contents
    content_rendered = template_env.from_string(page.content).render(**page.metadata)

    # convert all markdown to HTML if it exists
    htmlified = markdown.markdown(content_rendered, extensions=["attr_list", "fenced_code", "tables", "codehilite", "toc"])

    # Wrap in page template
    template_name = page.get('template', DEFAULT_TEMPLATE)
    template = template_env.get_template(f'{template_name}.html')

    return template.render( content=htmlified, **page.metadata)
    
# --- MAIN EXECUTION LOGIC ---

def create_output_directory():
    """Creates a clean output directory."""
    try:
        if OUTPUT_DIR.exists() and OUTPUT_DIR.is_dir():
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created clean output directory: {OUTPUT_DIR}")
    except Exception as e:
        print(f"Error creating output directory {OUTPUT_DIR}: \n{e}")
        return 


def create_files_from_pages(posts_list):
    """Take every every file in the pages folder and apply a template, convert to HTML, if not already, and place in the appropriate path in the docs folder."""

    for item in PAGES_DIR.rglob("*"):
        # Create the static path for the file/folder
        static_path = OUTPUT_DIR / item.relative_to(PAGES_DIR)
        # Create folders
        if item.is_dir():
            static_path.mkdir(parents=True, exist_ok=True) 
            continue

        # Create files
        # if file is an HTML file and has no YAML
        if item.suffix == ".html" and not frontmatter.check(item):
            # then copy as is without transformation 
            item.copy(static_path)
        else:
            prev_post, next_post = None, None

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
            static_path.with_suffix(".html").write_text(new_content, encoding='utf-8')

def create_post_index_page(posts_list):
    """Generates the main index page listing all posts."""
    if Path(PAGES_DIR/POSTS_DIR).is_dir() and Path(TEMPLATE_DIR/POST_INDEX_TEMPLATE).is_file():
        content = ''
        for post in posts_list:
            content += f"\n\t<a href='{BASE_URL}/{POSTS_DIR}/{post.get('filename', "")}'>{post.get('date', "")} - {post.get('title', "")}</a>"

        # load the content into a frontmatter object and add metadata
        page = frontmatter.loads(content)
        page['title'] = 'Posts Index Page'
        page['base_url'] = BASE_URL

        # Create the content using the template's content and the file's contents
        body_template = template_env.from_string(page.content)
        # Convert all of the jinja variables in the content
        resolved_content = body_template.render(**page.metadata)

        template_content = template_env.get_template(POST_INDEX_TEMPLATE)
        output = template_content.render(
            content=resolved_content,
            **page.metadata
        )

        Path(OUTPUT_DIR/POSTS_DIR/'index.html').write_text(output)
    else:
        return

def build_site():
    """Create directories, build static site files, copy files as necessary"""

    create_output_directory()

    posts_list = []
    if Path(PAGES_DIR/POSTS_DIR).is_dir():
        posts_list = get_sorted_posts()

    # Call the create_files_from function to create the pages
    create_files_from_pages(posts_list)

    if posts_list:
        create_post_index_page(posts_list)

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
    build_site()
