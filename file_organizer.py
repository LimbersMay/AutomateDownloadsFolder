import os
import pathlib
import shutil

from services.path_repository import PathRepository
from services.settings_repository import SettingsRepository


class FileOrganizer:
    def __init__(self, path_repository: PathRepository, settings_repository: SettingsRepository):
        self.path_repository = path_repository
        self.settings_repository = settings_repository

    def organize(self):

        # Paths
        source_path = self.path_repository.get_source_path().name
        destination_path = self.path_repository.get_destination_path().name

        # Configurations
        size_limit = self.settings_repository.get_settings().max_size

        with os.scandir(source_path) as it:
            full_paths = [entry.path for entry in it if entry.is_file()]

        # get files to organize based on the user configuration
        # 1. Sort files if size is greater than the user configuration
        files_to_organize = [file for file in full_paths if os.path.getsize(file) < size_limit]

        for file in files_to_organize:
            name_with_extension = pathlib.Path(file).name
            filename, extension = os.path.splitext(name_with_extension)

            # Check if the extension exists in the configuration
            destination_folder = self.settings_repository.find_extension_folder_name(extension)

            destination_file_path = os.path.join(destination_path, destination_folder.name, name_with_extension)

            # Move file to destination folder
            shutil.copy(file, destination_file_path)

        return None
