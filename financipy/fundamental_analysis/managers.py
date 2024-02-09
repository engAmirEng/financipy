from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from .models import MarketWatcherNotifModel
    from .types import TSETMCWatcherNotificationDataDict


class MarketWatcherNotifManager(models.Manager):
    def new_from_tsetmc(self, record: "TSETMCWatcherNotificationDataDict"):
        new_obj: "MarketWatcherNotifModel" = self.model()
        new_obj.original_title = record["title"]
        new_obj.original_body = record["body"]
        new_obj.publish_time = record["time"]
        new_obj.is_ready_to_be_announced = False
        new_obj.save()
        return new_obj
