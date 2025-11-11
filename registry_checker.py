import glob
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from send2trash import send2trash

from models.models import OrderedFile
from services.ordered_files_repository import OrderedFilesRepository
from services.path_repository import PathRepository
from services.settings_repository import SettingsRepository
from services.notification_service import NotificationService


class Auditor:
    def __init__(self, path_repository: PathRepository,
                 ordered_files_repository: OrderedFilesRepository,
                 settings_repository: SettingsRepository,
                 notificator_service: NotificationService):
        self.__path_repository = path_repository
        self.__ordered_files_repository = ordered_files_repository
        self.__settings_repository = settings_repository
        self.__notification_service = notificator_service

        self.__default_folder_name = self.__settings_repository.get_default_folder()

        self.__build_policy_map()

    def __build_policy_map(self):
        """Create a mapping of rule names to their lifecycle policies."""
        self.__policy_map = {}

        config = self.__settings_repository.get_app_config()

        # 1. Load policy rules of files
        for rule in config.sorting_rules:
            if rule.lifecycle:
                self.__policy_map[rule.folder_name] = rule.lifecycle

        # 2. Load folder policy rules
        for rule in config.folder_rules:
            if rule.lifecycle:
                self.__policy_map[rule.ruleName] = rule.lifecycle

        # 3. Load default policy
        self.__default_policy = config.default_lifecycle

        # 4. Policy for "Other"
        self.__policy_map[config.default_folder] = self.__default_policy


    def check_files(self):
        """"
        Check the files in the destination path against the lifecycle policies. Delete files that exceed the retention period and register new files.
        1. Check the files which exceed the limit days
        2. Register the files which are not registered in the database
        3. Send notification
        """

        # Paths
        destination_path = self.__path_repository.get_destination_path()

        items_deleted_count = 0
        items_to_remote_from_registry = []
        all_registered_items = self.__ordered_files_repository.get_ordered_files()

        # Create a map of registered paths for quick lookup
        registered_paths_map = {item.path: item for item in all_registered_items}

        # Process registered items first
        for item in all_registered_items:
            item_path = Path(item.path)

            # 1.1 Check if the file still exists
            if not item_path.exists():
                items_to_remote_from_registry.append(item)
                continue

            # 1.2 Check lifecycle policy
            policy = self.__policy_map.get(item.rule_name_applied, self.__default_policy)

            if policy and policy.enabled:
                days_expired = (datetime.now().date() - item.ordered_date).days

                if days_expired > policy.days_to_keep:
                    if policy.action == 'trash':
                        send2trash(item.path)
                    elif policy.action == 'delete':
                        if item_path.is_dir():
                            shutil.rmtree(item.path) # Remove directory and its contents
                        else:
                            os.remove(item.path) # Remove file

                    items_deleted_count += 1
                    items_to_remote_from_registry.append(item)


        # 2. Process unregistered items
        not_registered_items = []

        for physical_item_path in destination_path.rglob('*'):
            if str(physical_item_path) not in registered_paths_map:
                # 2.1 Determine rule name applied
                try:
                    rule_name = physical_item_path.relative_to(destination_path).parts[0]
                except IndexError:
                    rule_name = self.__default_folder_name

                new_item = OrderedFile(
                    name=physical_item_path.name,
                    ordered_date=datetime.now().date(),
                    path=str(physical_item_path),
                    rule_name_applied=rule_name
                )

                not_registered_items.append(new_item)

        # 3. Register unregistered items
        if not_registered_items:
            self.__ordered_files_repository.save_ordered_files(not_registered_items)

        # 3.1 Remove deleted items from registry
        if items_to_remote_from_registry:
            for item in items_to_remote_from_registry:
                self.__ordered_files_repository.delete(item)

        # 4. Send notification
        if items_deleted_count > 0:
            self.__notification_service.send_notification(f"{items_deleted_count} items have been deleted")