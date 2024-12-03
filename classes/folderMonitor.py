from watchdog.observers import Observer
from classes.fileEventHandler import FileEventHandler


# Folder Monitor Class
class FolderMonitor:
    def __init__(self, input_folder, file_handler, logger):
        self.input_folder = input_folder
        self.file_handler = file_handler
        self.logger = logger
        self.observer = Observer()

    def start(self):
        event_handler = FileEventHandler(self.file_handler, self.logger)
        self.observer.schedule(event_handler, self.input_folder, recursive=False)
        self.observer.start()
        self.logger.info("Started folder monitoring.")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.logger.info("Stopped folder monitoring.")