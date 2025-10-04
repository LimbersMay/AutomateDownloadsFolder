
class SortingRule:
    def __init__(self, folder_name: str, match_by: str, patterns: list[str]):
        self.folder_name = folder_name
        self.match_by = match_by
        self.patterns = patterns