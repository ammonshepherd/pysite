# Pysite
A static site generator written in python.

# Usage

Copy `pysite.py` and `server.py` files into your project directory.

## Setup
### Folders
Create the following directories/folders:

- layout/
- pages/
- posts/
- public/
- static_site/

The names of these directories can be changed in the `pysite.py` file.

### Files: Layout
Inside the layout folder, create the following files:

- layout/
    - `head.html` Contains the &lt;DOCTYPE&gt; tag, the &lt;html&gt; tag, the &lt;head&gt; and &lt;/head&gt; tags and any HTML that goes between, and the opening &lt;body&gt; tag.
    - `header.html` The &lt;header&gt; and &lt;/header&gt; tags and any HTML that goes in between. Top navigation is usually good to put here.
    - `foot.html` The &lt;footer&gt; and &lt;/footer&gt; tags and any HTML that goes in between, and any HTML that should go before the closing &lt;/body&gt; tag.
    - `footer.html` Just the closing &lt;/body&gt; and closing &lt;html&gt; tags. This could also have other HTML or Javascript that should be included before the closing &lt;/body&gt; tag.

These four files will be wrapped around every file in the `pages` and `posts` directories. If you don't want to use any of them, just leave them empty. At least the `head.html` and `foot.html` files must have content in them.

The names of these files can be changed in the `pysite.py` file.

### Files: Pages
These files contain the &lt;main&gt; and &lt;/main&gt; tags and anything that goes in between. This is the main content of the website.

HTML files inside the `pages` directory will be turned into HTML files to be served. Each file will have the head.html and header.html content prepended to it and the foot.html and footer.html content appended to it.

The combined HTML file is named the same as the filename in the pages directory. This will be served at the root level of the site. 

Subdirectories in the pages folder and files within those subdirectories will be recreated in the `static_site` directory.

### Files: Posts
These files contain the &lt;main&gt; and &lt;/main&gt; tags and anything that goes in between. This is the main content of the website.

Similar to the files in the pages directory, these files will have the content of the files in the layout directory prepended and appended to them.

All posts will go into the the `static_site/posts` directory.


### Files: Public
The files and folders in the `public` directory will be copied recursively to the static_sites folder without alteration.

This is where you put the images, css and Javascript. Suggested file structure:

- public/
  - css/
    - style.css
  - images/
    - logo.png
    - picture1.jpg
  - js/
    - menu.js

Access the files in these directories in your HTML as absolute paths:

The file public/images/logo.png is accessed like `</img src="/public/images/logo.png">`

The CSS file can be accessed in the layout/head.html file like `<link rel="stylesheet" href="/public/css/style.css" />`


## Running the script

After your files are created, run the following command in the terminal

```python server.py```

This will create the files in the `static_site` directory and start an HTML server. 

You can view the site at http://127.0.0.1:8000

The server will notice changes to files and restart the server every .5 seconds so you can refresh the browser to the latest changes.
