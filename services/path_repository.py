import json
from abc import ABC, abstractmethod
from pathlib import Path

from models.models import PathConfig


class PathRepository(ABC):

    @abstractmethod
    def get_source_path(self) -> Path:
        pass

    @abstractmethod
    def get_destination_path(self) -> Path:
        pass


class JsonPathRepository(PathRepository):

    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def get_source_path(self) -> Path:
        with open(self.json_file_path, "r") as json_file:
            destination_path = json.load(json_file)["paths"]["sourcePath"]

            return Path(destination_path)

    def get_destination_path(self) -> Path:
        with open(self.json_file_path, "r") as json_file:
            source_path = json.load(json_file)["paths"]["destinationPath"]

            return Path(source_path)

class ConfigPathRepository(PathRepository):

    def __init__(self, path_config: PathConfig):
        self.__config = path_config

    def get_source_path(self) -> Path:
        return self.__config.source_path

    def get_destination_path(self) -> Path:
        return self.__config.destination_path