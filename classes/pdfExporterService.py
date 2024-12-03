import os
import threading
import time

import win32service
import win32serviceutil

from classes.serviceLogger import ServiceLogger
from classes.configManager import ConfigManager
from classes.fileHandler import FileHandler
from classes.folderMonitor import FolderMonitor


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