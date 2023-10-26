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
    def get_extensions(self) -> List[str]:
        pass


class JsonSettingsRepository(SettingsRepository):

    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def get_settings(self) -> Settings:
        with open(self.json_file_path, "r") as json_file:
            json_data = json.load(json_file)["settings"]

            days_to_keep = json_data["daysToKeep"]
            wants_to_send_to_trash = json_data["wantsToSendToTrash"]
            max_size = json_data["maxSize"]
            extensions = self.get_extensions()

            return Settings(days_to_keep, wants_to_send_to_trash, max_size, extensions)

    def get_extensions(self) -> List[Extension]:
        with open(self.json_file_path, "r") as json_file:
            json_data = json.load(json_file)["extensions"]

            extensions = []

            # map from the object {"ExtensionName: [list of extensions]", ...} -> list of extensions
            for extension_name, extensions_formats in json_data.items():
                extensions.append(Extension(extension_name, extensions_formats))

            return extensions
