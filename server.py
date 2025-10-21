import os
import sys
import time
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration ---
WATCH_DIRECTORY = '.'            # The directory to watch for changes
BUILD_SCRIPT = "pysite.py"      # The script to execute on file change
SERVE_DIRECTORY = "static_site"       # The directory for the HTTP server to serve
SERVER_HOST = '127.0.0.1'        # The host address for the HTTP server
SERVER_PORT = 8000               # The port for the HTTP server

# --- Global variable for the server process ---
server_process = None

# --- File Change Handler ---
class ChangeHandler(FileSystemEventHandler):
    """Event handler that runs a build script on file system changes."""
    def __init__(self, build_script):
        self.build_script = build_script
        self.last_run_time = 0

    def on_any_event(self, event):
        # Ignore events on directories and the script itself
        if event.is_directory or event.src_path.endswith('server.py'):
            return

        # Simple debounce to prevent running the script multiple times for one save
        current_time = time.time()
        if current_time - self.last_run_time < 0.5:
            return
        
        self.last_run_time = current_time

        print(f"\nFile changed: {event.src_path}. Running build script...")
        self.run_script()
        print("Waiting for changes...")

    def run_script(self):
        """Runs the specified build script using subprocess."""
        try:
            # Use subprocess.run for a robust way to execute external commands
            subprocess.run(
                ["python", self.build_script], 
                check=True, 
                text=True, 
                capture_output=True
            )
            now = datetime.now()
            print(f"Build script executed successfully. {now}")
        except subprocess.CalledProcessError as e:
            print(f"Error running script:\n{e.stderr.strip()}")
        except FileNotFoundError:
            print(f"Error: Build script '{self.build_script}' not found.")

def start_http_server(host, port, directory):
    """Starts the HTTP server as a non-blocking subprocess."""
    print(f"Starting HTTP server at http://{host}:{port}")
    # The `-d` flag specifies the directory to serve files from.
    # The host and port must be passed as string arguments.
    command = [
        "python", 
        "-m", 
        "http.server", 
        str(port), 
        "--bind", 
        host,
        "--directory", 
        directory
    ]
    
    # Use Popen to start the process non-blocking.
    # The `start_new_session=True` flag helps with process cleanup.
    return subprocess.Popen(
        command, 
        start_new_session=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )

def stop_http_server(process):
    """Gracefully terminates the HTTP server subprocess."""
    if process and process.poll() is None:
        print("\nStopping HTTP server...")
        try:
            # First, try a graceful termination
            process.terminate()
            process.wait(timeout=5)  # Wait up to 5 seconds for cleanup
        except (subprocess.TimeoutExpired, ProcessLookupError):
            # If graceful termination fails, force kill
            print("Server did not terminate gracefully, forcing kill.")
            process.kill()
        print("Server stopped.")

def run_watcher():
    """Starts the file watcher and server."""
    global server_process

    # Perform an initial build
    print("Performing initial build...")
    ChangeHandler(BUILD_SCRIPT).run_script()
    
    # Start the HTTP server within a try-finally block
    try:
        server_process = start_http_server(SERVER_HOST, SERVER_PORT, SERVE_DIRECTORY)
        print(f"Watching for file changes in '{os.path.abspath(WATCH_DIRECTORY)}'...")
        
        # Create and schedule the file watcher
        event_handler = ChangeHandler(BUILD_SCRIPT)
        observer = Observer()
        observer.schedule(event_handler, path=WATCH_DIRECTORY, recursive=True)
        observer.start()

        # Keep the main thread alive to watch for events
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nWatcher interrupted by user.")
    finally:
        # This block ensures the server and watcher are stopped, even on an error
        if observer:
            observer.stop()
            observer.join()
        stop_http_server(server_process)
        print("Watcher stopped.")

if __name__ == "__main__":
    run_watcher()

