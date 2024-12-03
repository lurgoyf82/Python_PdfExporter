import time
from watchdog.events import FileSystemEventHandler


# File Event Handler Class
class FileEventHandler(FileSystemEventHandler):
    def __init__(self, file_handler, logger):
        self.file_handler = file_handler
        self.logger = logger

    def on_created(self, event):
        if event.is_directory:
            return
        # Wait for the file to be fully written
        time.sleep(5)
        self.logger.info(f"Detected new file: {event.src_path}")
        self.file_handler.process_file(event.src_path)