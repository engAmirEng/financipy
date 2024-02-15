from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from .models import MarketWatcherNotifModel, MarketWatcherNotifProfileModel
    from .types import TSETMCWatcherNotificationDataDict


class MarketWatcherNotifManager(models.Manager):
    def new_from_tsetmc(self, record: "TSETMCWatcherNotificationDataDict"):
        new_obj: "MarketWatcherNotifModel" = self.model()
        new_obj.original_title = record["title"]
        new_obj.original_body = record["body"]
        new_obj.publish_time = record["time"]
        new_obj.save()
        return new_obj


class MarketWatcherNotifProfileQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(status=self.model.Status.ACTIVE)


class MarketWatcherNotifProfileManager(models.Manager):
    def get_queryset(self):
        return MarketWatcherNotifProfileQuerySet(model=self.model, using=self._db, hints=self._hints)

    async def get_for_user(self, user) -> "MarketWatcherNotifProfileModel":
        obj, created = await self.aget_or_create(
            user=user, defaults={"status": self.model.Status.ACTIVE, "ai_boosted": True}
        )
        return obj
