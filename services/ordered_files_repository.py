import json
from abc import ABC, abstractmethod
from typing import List

from entities.ordered_file import OrderedFile


class OrderedFilesRepository(ABC):
    @abstractmethod
    def get_ordered_files(self):
        pass

    @abstractmethod
    def get_files_to_delete(self):
        pass

    @abstractmethod
    def set_new_ordered_files(self, new_ordered_files: List[OrderedFile]):
        pass


class JsonOrderedFilesRepository(OrderedFilesRepository):
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def get_ordered_files(self) -> List[OrderedFile]:

        with open(self.json_file_path, 'r') as json_file:
            json_data = json.load(json_file)["orderedFiles"]

            def get_ordered_file(item):
                name, ordered_date = item
                return OrderedFile(name, ordered_date)

            new_list = list(map(get_ordered_file, json_data.items()))

        return new_list


    def get_files_to_delete(self):
        pass

    def set_new_ordered_files(self, new_ordered_files: List[OrderedFile]):
        pass