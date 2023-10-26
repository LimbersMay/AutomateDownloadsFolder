from abc import ABC, abstractmethod


class PathRepository(ABC):

    @abstractmethod
    def get_source_path(self):
        pass

    @abstractmethod
    def get_destination_path(self):
        pass
