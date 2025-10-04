import datetime
import os
import pathlib
import re
import shutil
from typing import List

from entities.ordered_file import OrderedFile
from entities.sorting_rule import SortingRule
from services.ordered_files_repository import OrderedFilesRepository
from services.path_repository import PathRepository
from services.settings_repository import SettingsRepository
from services.notification_service import NotificationService


class FileSorter:
    def __init__(self, path_repository: PathRepository,
                 settings_repository: SettingsRepository,
                 ordered_files_repository: OrderedFilesRepository,
                 notificator_service: NotificationService):

        self.__path_repository = path_repository
        self.__settings_repository = settings_repository
        self.__ordered_files_repository = ordered_files_repository
        self.__notification_service = notificator_service

    def __find_destination_folder(self, file_name: str, rules: List[SortingRule], default_folder: str) -> str:
        """
            Find the destination folder for a given file based on sorting rules.
            :param file_name: Name of the file to be sorted.
            :param rules: List of sorting rules to apply.
            :param default_folder: Default folder name if no rules match.
            :return: The name of the destination folder.
        """
        _, extension = os.path.splitext(file_name)

        for rule in rules:
            print(f"Checking rule: {rule.folder_name} by {rule.match_by} with patterns {rule.patterns}")
            if rule.match_by == "extension":
                if extension.lower() in [p.lower() for p in rule.patterns]:
                    return rule.folder_name

            elif rule.match_by == "regex":
                for pattern in rule.patterns:
                    print(f"Matching {file_name} against pattern {pattern}")
                    if re.match(pattern, file_name):
                        print(f"Matched {file_name} against pattern {pattern}")
                        return rule.folder_name

        return default_folder

    def sort(self):

        # Paths
        source_path = self.__path_repository.get_source_path().name
        destination_path = self.__path_repository.get_destination_path().name

        # Configurations
        size_limit = self.__settings_repository.get_settings().max_size

        # Clasification rules and default folder
        sorting_rules = self.__settings_repository.get_sorting_rules()
        default_folder = self.__settings_repository.get_default_folder()

        with os.scandir(source_path) as it:
            full_paths = [entry.path for entry in it if entry.is_file()]

        # Get files to organize based on user configuration
        # 1. Sort files if size is greater than the user configuration
        files_to_organize = [file for file in full_paths if os.path.getsize(file) < size_limit]
        ordered_files: List[OrderedFile] = []

        for current_file_path in files_to_organize:
            name_with_extension = pathlib.Path(current_file_path).name

            # Example: "example.txt" -> "txt"
            destination_folder_name = self.__find_destination_folder(name_with_extension, sorting_rules, default_folder)

            # We make the final path if not exists
            # Example: destination_path/destination_folder_name
            destination_folder_path = os.path.join(destination_path, destination_folder_name)
            os.makedirs(destination_folder_path, exist_ok=True)

            destination_file_path = os.path.join(destination_folder_path, name_with_extension)

            shutil.move(current_file_path, destination_file_path)

            # Map the files to OrderedFiles objects
            current_date = datetime.datetime.now().date()
            ordered_files.append(OrderedFile(name_with_extension, current_date, destination_file_path))

        # Persist the new ordered files
        if ordered_files:
            self.__ordered_files_repository.save_ordered_files(ordered_files)

        # 2. Send notification
        if len(files_to_organize) > 0:
            self.__notification_service.send_notification(f"{len(files_to_organize)} files were sorted")
