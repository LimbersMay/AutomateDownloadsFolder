from typing import List


class Extension:
    def __init__(self, name: str, extensions: List[str]):
        self.name = name
        self.extensions = extensions
