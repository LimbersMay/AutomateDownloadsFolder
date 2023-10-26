from typing import List

from entities.extension import Extension


class Settings:
    def __init__(self, days_to_keep: int, wants_to_send_to_trash: bool, max_size: int, extensions: List[Extension]):
        self.days_to_keep = days_to_keep
        self.wants_to_send_to_trash = wants_to_send_to_trash
        self.max_size = max_size
        self.extensions = extensions
