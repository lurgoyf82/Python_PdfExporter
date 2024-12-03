import os
import json

class JsonFileManager:
    """
    A generic class to handle saving and loading objects to and from JSON files.
    """

    configmanager = None

    def __init__(self, config_manager):
        """
        Initializes the JsonFileManager with a ConfigurationManager.

        :param config_manager: An instance of ConfigurationManager to provide configuration details.
        """
        self.config_manager = config_manager

        # Get the JSON schema directory from the configuration manager
        self.base_directory = self.config_manager.get("JSON_SCHEMA_DIRECTORY")
        if not self.base_directory:
            raise ValueError("Configuration missing: 'JSON_SCHEMA_DIRECTORY'")

        # Ensure the full directory exists AFTER joining
        os.makedirs(self.base_directory, exist_ok=True)

        # Print out the correct final path
        print(f"JSON schema directory: {self.base_directory}")

    def save(self, obj, file_name: str):
        """
        Saves a serializable object to a JSON file.

        :param obj: The object to save, which must have a `to_dict` method.
        :param file_name: The name of the JSON file (without directory path).
        """
        if not hasattr(obj, 'to_dict'):
            raise TypeError("Object must implement a 'to_dict' method for serialization.")

        file_path = os.path.join(self.base_directory, file_name)

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(obj.to_dict(), json_file, ensure_ascii=False, indent=4)

    def load(self, file_name: str, obj_class):
        """
        Loads a JSON file and reconstructs an object using the given class.

        :param file_name: The name of the JSON file (without directory path).
        :param obj_class: The class to reconstruct the object from, which must implement a `from_dict` method.
        :return: An instance of obj_class reconstructed from the JSON file.
        """
        file_path = os.path.join(self.base_directory, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        if not hasattr(obj_class, 'from_dict'):
            raise TypeError("Object class must implement a 'from_dict' method for deserialization.")

        return obj_class.from_dict(data)