from typing import List

from entities.sorting_rule import SortingRule


class Settings:
    def __init__(self, days_to_keep: int, send_to_trash: bool, max_size: int, sorting_rules: List[SortingRule]):
        self.days_to_keep = days_to_keep
        self.send_to_trash = send_to_trash
        self.max_size = max_size
        self.sorting_rules = sorting_rules
