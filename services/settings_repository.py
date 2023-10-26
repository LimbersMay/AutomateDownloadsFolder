from abc import ABC, abstractmethod
from typing import List


class SettingsRepository:

    @abstractmethod
    def get_days_to_keep(self) -> int:
        pass

    @abstractmethod
    def get_wants_to_send_to_trash(self) -> bool:
        pass

    @abstractmethod
    def get_max_size(self) -> int:
        pass

    @abstractmethod
    def get_extensions_folder_name(self) -> List[str]:
        pass
