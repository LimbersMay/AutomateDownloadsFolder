import datetime
import fnmatch
import os
import pathlib
import re
import shutil
from importlib.util import source_hash
from typing import List, Optional

from send2trash import send2trash

from models.app_config import ZoneConfig
from models.models import SortingRule, OrderedFile
from services.ordered_files_repository import OrderedFilesRepository
from services.path_repository import PathRepository
from services.settings_repository import SettingsRepository
from services.notification_service import NotificationService


class FileSorter:
    def __init__(self, path_repository: PathRepository,
                 settings_repository: SettingsRepository,
                 ordered_files_repository: OrderedFilesRepository,
                 notificator_service: NotificationService,
                 zone_config: ZoneConfig):

        self.__path_repository = path_repository
        self.__settings_repository = settings_repository
        self.__ordered_files_repository = ordered_files_repository
        self.__notification_service = notificator_service
        self.__zone_config = zone_config

        settings = settings_repository.get_settings()

        self.__source_path = path_repository.get_source_path()
        self.__destination_path = path_repository.get_destination_path()

        # Files config
        self.__size_limit = settings.max_size_in_mb

        # Rules config
        self.__sorting_rules: List[SortingRule] = self.__settings_repository.get_sorting_rules()

        # Track list
        self.__newly_tracked_items: List[OrderedFile] = []

        # For files/folders moved but not tracked, for notification purposes
        self.__untracked_items_counter = 0


    def sort(self):
        # 1. Clean up the newly tracked items list
        self.__newly_tracked_items = []
        self.__untracked_items_counter = 0

        source_path = self.__path_repository.get_source_path()
        destination_path = self.__path_repository.get_destination_path()
        abs_destination_path = destination_path.resolve()

        for root, directories, files in os.walk(source_path):
            root_path = pathlib.Path(root)

            # Check if we are in the root path
            is_surface = (root_path == source_path)

            dirs_to_keep = []

            for directory in directories:
                directory_path = root_path / directory

                # 1.1 Protect the destination path
                if self.__is_protected_path(directory_path, abs_destination_path):
                    continue

                # 1.2 Find the matching rule for the directory
                rule = self.__find_matching_rule(directory_path)

                # If ignored, cut the tree
                if rule and rule.handling_strategy == 'ignore':
                    continue

                is_recursive = rule and getattr(rule, 'search_scope', 'surface') == 'recursive'

                # 1.3 If is a folder we must process
                if rule and (is_surface or is_recursive):
                    self.__process_folder(directory_path, rule)

                    if rule.handling_strategy in ['move', 'process_contents']:
                        continue

                # 1.4 If the folder is clean we keep it
                dirs_to_keep.append(directory)

            directories[:] = dirs_to_keep

            for file in files:
                file_path = root_path / file

                if self.__is_protected_path(file_path, abs_destination_path):
                    continue

                rule = self.__find_matching_rule(file_path)

                if not rule or rule.handling_strategy == 'ignore':
                    continue

                is_recursive = rule and getattr(rule, 'search_scope', 'surface') == 'recursive'

                if is_surface or is_recursive:
                    self.__process_file(file_path, rule)

        if self.__newly_tracked_items:
            self.__ordered_files_repository.save_ordered_files(self.__newly_tracked_items)
            self.__notification_service.send_notification(f"{len(self.__newly_tracked_items)} files were sorted from {self.__zone_config.zone_name} zone")

        if self.__untracked_items_counter > 0:
            self.__notification_service.send_notification(
                f"{self.__untracked_items_counter} items were moved but not tracked from {self.__zone_config.zone_name} zone")


    def __is_protected_path(self, item_path: pathlib.Path, protected_path: pathlib.Path) -> bool:
        """
        Check if the given item path is the same as or a subpath of the protected path.

        :param item_path: The path of the item to check.
        :param protected_path: The path that should be protected (e.g., destination folder).
        :return: True if the item path is the same as or a subpath of the protected path, False otherwise.
        """
        try:
            # Resolve both paths to their absolute forms
            abs_item_path = item_path.resolve()
            abs_protected_path = protected_path.resolve()

            # Check if the item path is exactly the same as the protected path
            if abs_item_path == abs_protected_path:
                return True

            # Check if the item path is a subpath of the protected path
            if abs_protected_path.is_relative_to(abs_item_path):
                return True

            return False

        except Exception as e:
            print(f"Error checking protected path for {item_path}: {e}")
            return False

    def __process_file(self, file_path: pathlib.Path, rule: Optional[SortingRule] = None):
        """
        Process a single file: determine its destination folder, move it, and track it.
        1. Check the file size.
        2. Find the rule that matches the file.
        3. Move the file to the destination folder.
        4. Track the file.

        :param file_path: Path of the file to process.
        :return: None

        """

        # 1. Check if file exists
        if not file_path.exists():
            return

        # 2. Check file size
        if file_path.stat().st_size >= (self.__size_limit * 1024 * 1024):
            return

        # 3.1 Check if handling strategy is ignore
        if not rule or rule.handling_strategy == 'ignore':
            return

        destination_folder_name = rule.destination_folder

        # 4. Create destination path and move file
        destination_folder_path = self.__destination_path / destination_folder_name
        destination_folder_path.mkdir(parents=True, exist_ok=True)
        final_file_path = destination_folder_path / file_path.name

        try:
            shutil.move(str(file_path), str(final_file_path))

            # 5. Track the moved file if lifecycle is enabled
            has_active_lifecycle = rule and rule.lifecycle and rule.lifecycle.enabled

            if not has_active_lifecycle:
                self.__untracked_items_counter += 1
                return

            items_to_track = OrderedFile(
                name=file_path.name,
                ordered_date=datetime.datetime.now().date(),
                path=str(final_file_path),
                rule_name_applied=rule.rule_name,
            )

            self.__newly_tracked_items.append(items_to_track)

        except Exception as e:
            print(f"Error moving file {file_path} to {final_file_path}: {e}")

    def __process_folder(self, folder_path: pathlib.Path, rule: Optional[SortingRule] = None):
        if not folder_path.exists():
            return

        if not rule:
            return

        action = rule.handling_strategy

        if action == 'ignore':
            return

        elif action == 'process_contents':

            # 1. Validate destination folder
            if not rule or not rule.destination_folder:
                return

            # 2. Process each file in the folder
            for sub_item in folder_path.rglob('*'):
                sub_rule = self.__find_matching_rule(sub_item)
                if sub_item.is_file():
                    self.__process_file(sub_item, sub_rule)

            # 3. Delete the empty folder if specified
            if rule and rule.delete_empty_after_processing:
                try:
                    send2trash(str(folder_path))
                except Exception as e:
                    print(f"Error deleting non-empty folder {folder_path}: {e}")

        elif action == 'move':
            destination_base = self.__path_repository.get_destination_path()
            destination_folder = rule.destination_folder if rule.destination_folder else 'Folders'

            final_destination_path = destination_base / destination_folder / folder_path.name

            # Ensure the destination folder exists
            (destination_base / destination_folder).mkdir(exist_ok=True, parents=True)

            try:
                shutil.move(str(folder_path), str(final_destination_path))
                if rule and rule.lifecycle and rule.lifecycle.enabled:
                    items_to_track = OrderedFile(
                        name=folder_path.name,
                        ordered_date=datetime.datetime.now().date(),
                        path=str(final_destination_path),
                        rule_name_applied=action,
                    )
                    self.__newly_tracked_items.append(items_to_track)

                else:
                    self.__untracked_items_counter += 1
            except Exception as e:
                print(f"Error moving folder {folder_path} to {final_destination_path}: {e}")

    def __find_matching_rule(self, item_path: pathlib.Path) -> Optional[SortingRule]:
        """"
        Find the first sorting rule that matches the given item name.
        """
        item_name = item_path.name
        source_path = self.__path_repository.get_source_path()
        for rule in self.__sorting_rules:
            if rule.match_by == "extension":
                _, extension = os.path.splitext(item_name)
                if extension.lower() in [p.lower() for p in rule.patterns]:
                    return rule
            elif rule.match_by == "regex":
                for pattern in rule.patterns:
                    if re.match(pattern, item_name):
                        return rule
            elif rule.match_by == "glob":
                # Try to calculate relative path to support patterns like "**/temp/*.pdf"
                try:
                    rel_path_str = item_path.relative_to(source_path).as_posix()
                except ValueError:
                    rel_path_str = item_name

                for pattern in rule.patterns:
                    if item_path.match(pattern):
                        return rule

                    if fnmatch.fnmatch(item_name, pattern) or fnmatch.fnmatch(rel_path_str, pattern):
                        return rule
        return None