import os
import datetime
import json

class FolderStructureCreator:
    """
    A class to create folder structures based on provided data.
    """

    def __init__(self, config_manager):
        """
        Initialize the FolderStructureCreator with a base folder.
        Args:
            base_folder (str): The root directory for folder creation.
        """
        self.base_folder = config_manager.get("SRC_DIRECTORY")

    @staticmethod
    def get_current_datetime_formatted():
        """
        Get the current date-time in the format yyyy_mm_dd_HH_MM_SS.
        Returns:
            str: Formatted date-time string.
        """
        return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def create_structure(self, folder_structure):
        """
        Creates the folder structure based on the provided dictionary.
        Args:
            folder_structure (dict): Dictionary representing the folder structure.
        Returns:
            str: The path to the created folder structure.
        """
        # Create the base path with the current date-time
        current_datetime = self.get_current_datetime_formatted()
        base_path = os.path.join(self.base_folder, current_datetime)

        # Recursively create the folder structure
        self._create_folders(base_path, folder_structure)

        print(f"Folder structure created at: {base_path}")
        return base_path

    def _create_folders(self, current_path, structure):
        """
        Helper method to recursively create folders.
        Args:
            current_path (str): The current path where folders will be created.
            structure (dict): The nested dictionary representing folder structure.
        """
        for folder_name, subfolders in structure.items():
            folder_path = os.path.join(current_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            if isinstance(subfolders, dict):
                self._create_folders(folder_path, subfolders)
