import datetime


class OrderedFile:
    def __init__(self, name: str, ordered_date: datetime.date, path: str):
        self.name = name
        self.ordered_date = ordered_date
        self.path = path
