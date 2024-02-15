import datetime
from typing import TypedDict


class TSETMCWatcherNotificationDataDict(TypedDict):
    title: str
    body: str
    time: datetime.datetime
