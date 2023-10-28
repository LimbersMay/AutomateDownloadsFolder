import datetime
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from entities.ordered_file import OrderedFile


class OrderedFilesRepository(ABC):
    @abstractmethod
    def get_ordered_files(self) -> List[OrderedFile]:
        pass

    @abstractmethod
    def get_files_to_delete(self, days_to_keep: int) -> List[OrderedFile]:
        pass

    @abstractmethod
    def set_new_ordered_files(self, new_ordered_files: List[OrderedFile]) -> None:
        pass

    @abstractmethod
    def find(self, file_name: str) -> OrderedFile or None:
        pass

    @abstractmethod
    def delete(self, file_name: str) -> None:
        pass


class JsonOrderedFilesRepository(OrderedFilesRepository):
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def get_ordered_files(self) -> List[OrderedFile]:
        with open(self.json_file_path, 'r') as json_file:
            json_data = json.load(json_file)["orderedFiles"]

            ordered_files = []

            # map from the objects {{name: date}, ...} -> OrderedFile object
            for fileObject in json_data:
                name = fileObject["name"]
                ordered_date = fileObject["ordered_date"]
                path = fileObject["path"]

                ordered_date = datetime.strptime(ordered_date, "%Y-%m-%d").date()
                ordered_files.append(OrderedFile(name, ordered_date, path))

            return ordered_files

    def get_files_to_delete(self, days_to_keep: int) -> List[OrderedFile]:
        ordered_files = self.get_ordered_files()
        files_to_delete = []

        for ordered_file in ordered_files:
            current_date = datetime.now().date()
            if (current_date - ordered_file.ordered_date).days > days_to_keep:
                files_to_delete.append(ordered_file)

        return files_to_delete

    def set_new_ordered_files(self, new_ordered_files: List[OrderedFile]) -> None:
        ordered_files = self.get_ordered_files()
        ordered_files.extend(new_ordered_files)

        # Convert the date objects to the iso format
        for i in range(len(ordered_files)):
            ordered_files[i].ordered_date = ordered_files[i].ordered_date.isoformat()

        # load the json data in a file
        with open(self.json_file_path, "r") as json_file:
            data = json.load(json_file)

        data["orderedFiles"] = [obj.__dict__ for obj in ordered_files]

        with open(self.json_file_path, "w") as json_file:
            json_file.write(json.dumps(data, indent=4))

    def find(self, file_name: str) -> OrderedFile or None:
        ordered_files = self.get_ordered_files()

        for ordered_file in ordered_files:
            if ordered_file.name == file_name:
                return ordered_file

        return None

    def delete(self, file_name: str) -> None:
        with open(self.json_file_path, "r") as json_file:
            data = json.load(json_file)

            ordered_files = data["orderedFiles"]

            for file in ordered_files:
                if file["name"] == file_name:
                    ordered_files.remove(file)
                    break

        with open(self.json_file_path, "w") as json_file:
            json_file.write(json.dumps(data, indent=4))
