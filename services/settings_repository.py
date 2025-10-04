import json
from abc import ABC, abstractmethod
from typing import List

from entities.settings import Settings
from entities.sorting_rule import SortingRule


class SettingsRepository(ABC):

    @abstractmethod
    def get_settings(self) -> Settings:
        pass

    @abstractmethod
    def get_sorting_rules(self) -> List[SortingRule]:
        pass

    @abstractmethod
    def get_default_folder(self) -> str:
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
            sorting_rules = self.get_sorting_rules()

            return Settings(days_to_keep, send_to_trash, max_size, sorting_rules)

    def get_sorting_rules(self) -> List[SortingRule]:
        with open(self.json_file_path, "r") as json_file:
            json_data = json.load(json_file)["sortingRules"]

            sorting_rules = []

            for sorting_rule in json_data:
                folder_name = sorting_rule["folderName"]
                match_by = sorting_rule["matchBy"]
                patterns = sorting_rule["patterns"]

                sorting_rules.append(SortingRule(folder_name, match_by, patterns))

        return sorting_rules

    def get_default_folder(self) -> str:
        with open(self.json_file_path, "r") as json_file:
            json_data = json.load(json_file)["defaultFolder"]
            return json_data