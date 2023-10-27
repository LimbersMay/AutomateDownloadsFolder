import datetime
import os
import pathlib
import shutil
from typing import List

from entities.extension import Extension
from entities.ordered_file import OrderedFile
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

    def sort(self):

        # Paths
        source_path = self.__path_repository.get_source_path().name
        destination_path = self.__path_repository.get_destination_path().name

        # Configurations
        size_limit = self.__settings_repository.get_settings().max_size

        with os.scandir(source_path) as it:
            full_paths = [entry.path for entry in it if entry.is_file()]

        # get files to organize based on the user configuration
        # 1. Sort files if size is greater than the user configuration
        files_to_organize = [file for file in full_paths if os.path.getsize(file) < size_limit]
        ordered_files: List[OrderedFile] = []

        for file_path in files_to_organize:
            name_with_extension = pathlib.Path(file_path).name
            filename, extension = os.path.splitext(name_with_extension)

            destination_folder: Extension = self.__settings_repository.find_extension_folder_name(extension)
            destination_file_path: str = os.path.join(destination_path, destination_folder.name, name_with_extension)

            shutil.move(file_path, destination_file_path)

            # Map the files to OrderedFiles objects
            current_date = datetime.datetime.now().date()
            ordered_files.append(OrderedFile(name_with_extension, current_date, destination_file_path))

        # Persist the new ordered files
        self.__ordered_files_repository.set_new_ordered_files(ordered_files)

        # 2. Send notification
        if len(files_to_organize) > 0:
            self.__notification_service.send_notification(f"{len(files_to_organize)} files were sorted")
