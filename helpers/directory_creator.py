import os

from services.path_repository import PathRepository
from services.settings_repository import SettingsRepository


class DirectoryCreator:
    def __init__(self, path_repository: PathRepository, settings_repository: SettingsRepository):
        self.__path_repository = path_repository
        self.__settings_repository = settings_repository

    def execute(self) -> None:
        destination_path = self.__path_repository.get_destination_path().name
        sorting_rules = self.__settings_repository.get_sorting_rules()

        for rule in sorting_rules:
            os.makedirs(os.path.join(destination_path, rule.folder_name), exist_ok=True)
