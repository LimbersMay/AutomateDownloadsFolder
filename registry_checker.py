import glob
import os
from datetime import datetime
from typing import List

from send2trash import send2trash

from entities.ordered_file import OrderedFile
from services.ordered_files_repository import OrderedFilesRepository
from services.path_repository import PathRepository
from services.settings_repository import SettingsRepository


class Auditor:
    def __init__(self, path_repository: PathRepository,
                 ordered_files_repository: OrderedFilesRepository,
                 settings_repository: SettingsRepository):
        self.__path_repository = path_repository
        self.__ordered_files_repository = ordered_files_repository
        self.__settings_repository = settings_repository

    def check_files(self):

        # Paths
        destination_path = self.__path_repository.get_destination_path().name

        # Settings
        limit_days = self.__settings_repository.get_settings().days_to_keep
        send_to_trash = self.__settings_repository.get_settings().send_to_trash

        # 1. Check the files which exceed the limit days
        files_to_delete = self.__ordered_files_repository.get_files_to_delete(limit_days)

        for file_to_delete in files_to_delete:

            # If the file registered in the database does not exist, we delete it from the DB and continue
            if not os.path.exists(file_to_delete.path):
                self.__ordered_files_repository.delete(file_to_delete.name)
                continue

            if send_to_trash:
                send2trash(file_to_delete.path)
            else:
                os.remove(file_to_delete.path)

            self.__ordered_files_repository.delete(file_to_delete.name)

        # 2. Register the files which are not registered in the database
        destination_paths = glob.glob(destination_path + "/**/*.*", recursive=True)
        destination_path_files = [os.path.basename(file) for file in destination_paths]

        not_registered_files: List[OrderedFile] = []

        for file, file_path in zip(destination_path_files, destination_paths):
            current_date = datetime.now().date()

            if not self.__ordered_files_repository.find(file):
                not_registered_files.append(OrderedFile(file, current_date, file_path))

        self.__ordered_files_repository.set_new_ordered_files(not_registered_files)
