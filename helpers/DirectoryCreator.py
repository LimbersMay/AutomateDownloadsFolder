import os


def create_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)


class DirectoryCreator:
    def __init__(self):
        pass

