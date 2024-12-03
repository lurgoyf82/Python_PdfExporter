import os
import sys
import time
import json
import logging
import threading
import shutil

from sqlalchemy.sql.functions import concat
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32serviceutil
import win32service
import win32event
import servicemanager

# Configuration Manager Class
class ConfigManager:
    def __init__(self, config_file, logger):
        self.config_file = config_file
        self.logger = logger
        self.config = {}
        self.load_config()

    def load_config(self):
        try:
            if not os.path.exists(self.config_file):
                self.create_default_config()
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            self.logger.info("Configuration loaded successfully.")
        except Exception as e:
            self.logger.exception(f"Failed to load configuration: {e}")
            self.config = {}
            self.create_default_config()

    def create_default_config(self):
        default_config = {
            "input_folder": r"C:\Program Files\PdfExporter\Input",
            "destination_folder": r"\\NAS\Shared\Destination",
            "waiting_folder": r"C:\Program Files\PdfExporter\Waiting",
            "error_folder": r"C:\Program Files\PdfExporter\Error"
        }
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        self.logger.info("Default configuration created.")
        self.config = default_config

    def get_input_folder(self):
        return self.config.get('input_folder')

    def get_destination_folder(self):
        return self.config.get('destination_folder')

    def get_waiting_folder(self):
        return self.config.get('waiting_folder')

    def get_error_folder(self):
        return self.config.get('error_folder')

    def get_current_progressive_number(self):
        return self.config.get(concat('progressive_number_', time.strftime('%Y')))

# Logger Class
class ServiceLogger:
    def __init__(self, log_file):
        self.setup_logging(log_file)

    def setup_logging(self, log_file):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger()

    def get_logger(self):
        return self.logger

# File Handler Class
class FileHandler:
    def __init__(self, config_manager, logger):
        self.config_manager = config_manager
        self.logger = logger

    def process_file(self, src_path):
        try:
            filename = os.path.basename(src_path)
            # Check if it's a PDF file
            if not filename.lower().endswith('.pdf'):
                self.logger.info(f"Skipping non-PDF file: {filename}")
                return

            # Renaming logic, e.g., prefix with timestamp
            new_filename = self.rename_file(filename)
            temp_path = os.path.join(self.config_manager.get_input_folder(), new_filename)
            os.rename(src_path, temp_path)  # Rename the file in the input folder

            # Try to move to destination folder
            dest_path = os.path.join(self.config_manager.get_destination_folder(), new_filename)
            try:
                shutil.move(temp_path, dest_path)
                self.logger.info(f"Moved file {new_filename} to destination folder.")
            except Exception as e:
                self.logger.warning(f"Failed to move file to destination: {e}")
                # Move to waiting folder instead
                waiting_path = os.path.join(self.config_manager.get_waiting_folder(), new_filename)
                shutil.move(temp_path, waiting_path)
                self.logger.info(f"Moved file {new_filename} to waiting folder.")

        except Exception as e:
            self.logger.exception(f"Error processing file {src_path}: {e}")
            # Move file to error folder
            error_folder = self.config_manager.get_error_folder()
            os.makedirs(error_folder, exist_ok=True)
            error_path = os.path.join(error_folder, filename)
            try:
                shutil.move(src_path, error_path)
                self.logger.info(f"Moved file {filename} to error folder.")
            except Exception as e:
                self.logger.exception(f"Failed to move file to error folder: {e}")

    def rename_file(self, filename):
        # Implement your renaming logic here
        # For example, prefix with timestamp

        #read current progressive number from json config file



        timestamp = time.strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"






        return new_filename

    def resend_waiting_files(self):
        waiting_folder = self.config_manager.get_waiting_folder()
        if not os.path.exists(waiting_folder):
            return  # Nothing to do
        for filename in os.listdir(waiting_folder):
            waiting_file_path = os.path.join(waiting_folder, filename)
            dest_path = os.path.join(self.config_manager.get_destination_folder(), filename)
            try:
                shutil.move(waiting_file_path, dest_path)
                self.logger.info(f"Resent file {filename} from waiting folder to destination.")
            except Exception as e:
                self.logger.warning(f"Failed to resend file {filename}: {e}")
                continue

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

# File Event Handler Class
class FileEventHandler(FileSystemEventHandler):
    def __init__(self, file_handler, logger):
        self.file_handler = file_handler
        self.logger = logger

    def on_created(self, event):
        if event.is_directory:
            return
        # Wait for the file to be fully written
        time.sleep(1)
        self.logger.info(f"Detected new file: {event.src_path}")
        self.file_handler.process_file(event.src_path)

# Main Service Class
class PdfExporterService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PdfExporterService"
    _svc_display_name_ = "PDF Exporter Service"
    _svc_description_ = "Monitors a folder and moves PDF files to a NAS."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = threading.Event()
        self.log_file = r"C:\Program Files\PdfExporter\service.log"
        self.config_file = r"C:\Program Files\PdfExporter\config.json"

        # Initialize Logger
        self.logger = ServiceLogger(self.log_file).get_logger()

        # Initialize Config Manager
        self.config_manager = ConfigManager(self.config_file, self.logger)

        # Initialize File Handler
        self.file_handler = FileHandler(self.config_manager, self.logger)

        # Initialize Folder Monitor
        self.input_folder = self.config_manager.get_input_folder()
        self.folder_monitor = FolderMonitor(self.input_folder, self.file_handler, self.logger)

    def SvcStop(self):
        self.logger.info("Service is stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_event.set()
        self.folder_monitor.stop()
        self.logger.info("Service stopped.")

    def SvcDoRun(self):
        self.logger.info("Service is starting...")
        try:
            self.main()
        except Exception as e:
            self.logger.exception(f"Service failed with exception: {e}")
            raise

    def main(self):
        # Ensure directories exist
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.config_manager.get_destination_folder(), exist_ok=True)
        os.makedirs(self.config_manager.get_waiting_folder(), exist_ok=True)
        os.makedirs(self.config_manager.get_error_folder(), exist_ok=True)

        # Start folder monitoring
        self.folder_monitor.start()

        # Start periodic task to resend waiting files
        while not self.stop_event.is_set():
            self.file_handler.resend_waiting_files()
            # Wait for some time before checking again
            time.sleep(1)  # Wait 1 second

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Running as a service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PdfExporterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Command-line options
        win32serviceutil.HandleCommandLine(PdfExporterService)
