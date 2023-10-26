import datetime


class OrderedFile:
    def __init__(self, name: str, ordered_date: datetime.date):
        self.name = name
        self.ordered_date = ordered_date
