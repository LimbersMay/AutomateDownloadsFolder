import json
from abc import ABC, abstractmethod
from typing import List

from entities.extension import Extension
from entities.settings import Settings


class SettingsRepository(ABC):

    @abstractmethod
    def get_settings(self) -> Settings:
        pass

    @abstractmethod
    def get_extensions(self) -> List[Extension]:
        pass

    @abstractmethod
    def find_extension_folder_name(self, extension_to_find: str) -> Extension:
        pass


class JsonSettingsRepository(SettingsRepository):

    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def get_settings(self) -> Settings:
        with open(self.json_file_path, "r") as json_file:
            json_data = json.load(json_file)["settings"]

            days_to_keep = json_data["daysToKeep"]
            send_to_trash = json_data["sendToTrash"]
            max_size = json_data["maxSizeInMb"] * (1024 * 1024)
            extensions = self.get_extensions()

            return Settings(days_to_keep, send_to_trash, max_size, extensions)

    def get_extensions(self) -> List[Extension]:
        with open(self.json_file_path, "r") as json_file:
            json_data = json.load(json_file)["extensions"]

            extensions = []

            # map from the object {"ExtensionName: [list of str]", ...} -> list of extensions
            for extension_name, extensions_formats in json_data.items():
                extensions.append(Extension(extension_name, extensions_formats))

            return extensions

    def find_extension_folder_name(self, extension_to_find: str) -> Extension:
        extensions = self.get_extensions()

        for founded_extensions in extensions:
            if founded_extensions.extensions.count(extension_to_find) > 0:
                return founded_extensions

        # If the extension is not found, we return the default extension
        default_extension = [extension for extension in extensions if len(extension.extensions) == 0][0]

        return default_extension
