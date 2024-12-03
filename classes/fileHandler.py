import os
import shutil
import time
import classes.configManager as configManager

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

        # read current progressive number from json config file

        timestamp = time.strftime('%Y%m%d')

        new_filename = f"Prog_{self.config_manager.get_current_progressive_number()}_{filename}_{timestamp}"

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