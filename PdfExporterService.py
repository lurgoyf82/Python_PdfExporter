import os
import sys
import time
import json
import logging
import threading
import win32serviceutil
import win32service
import win32event
import servicemanager
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from win10toast import ToastNotifier

from config.configuration_manager import ConfigurationManager


class PdfExporterService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PdfExporterService"
    _svc_display_name_ = "PDF Exporter Notification Service"
    _svc_description_ = "Monitors a folder and sends notifications for new files."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = threading.Event()
        self.input_dir = r"C:\Program Files\PdfExporter\Input"
        self.config_file = r"C:\Program Files\PdfExporter\config.json"
        self.log_file = r"C:\Program Files\PdfExporter\service.log"
        self.setup_logging()
        self.notifier = ToastNotifier()
        self.observer = Observer()





    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger()

    def SvcStop(self):
        self.logger.info("Service is stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_event.set()
        self.observer.stop()
        self.logger.info("Service stopped.")

    def SvcDoRun(self):
        self.logger.info("Service is starting...")
        try:
            self.main()
        except Exception as e:
            self.logger.exception(f"Service failed with exception: {e}")
            raise

    def main(self):
        # Ensure directories and config file exist
        os.makedirs(self.input_dir, exist_ok=True)
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f)

        event_handler = FileEventHandler(
            input_dir=self.input_dir,
            config_file=self.config_file,
            notifier=self.notifier,
            logger=self.logger
        )
        self.observer.schedule(event_handler, self.input_dir, recursive=False)
        self.observer.start()
        self.logger.info("Started monitoring folder.")

        while not self.stop_event.is_set():
            time.sleep(1)

        self.observer.join()

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, input_dir, config_file, notifier, logger):
        self.input_dir = input_dir
        self.config_file = config_file
        self.notifier = notifier
        self.logger = logger
        self.load_config()

        config = ConfigurationManager();

        self.input_dir = config.get("INPUT_DIR");
        self.config_file = config.get("CONFIG_FILE");
        self.notifier = config.get("NOTIFIER");

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError:
            self.config = {}
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def on_created(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        if filename not in self.config:
            self.config[filename] = True
            self.save_config()
            self.send_notification(filename)
            self.logger.info(f"Detected new file: {filename}")

    def on_deleted(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        if filename in self.config:
            del self.config[filename]
            self.save_config()
            self.logger.info(f"File deleted: {filename}")

    def send_notification(self, filename):
        try:
            self.notifier.show_toast(
                "New File Detected",
                f"A new file '{filename}' has been added.",
                duration=5,
                threaded=True
            )
        except Exception as e:
            self.logger.exception(f"Failed to send notification for {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Running as a service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PdfExporterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Called directly
        win32serviceutil.HandleCommandLine(PdfExporterService)
