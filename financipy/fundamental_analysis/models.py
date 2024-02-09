from django.db import models
from django.utils.translation import gettext_lazy as __

from financipy.core.models import BaseFeatureModel, MarketType
from financipy.fundamental_analysis.managers import MarketWatcherNotifManager
from financipy.utils.models import TimeStampedModel


class MarketWatcherNotifModel(TimeStampedModel, models.Model):
    original_title = models.CharField(max_length=255)
    original_body = models.TextField()
    publish_time = models.DateTimeField()
    ai_title = models.CharField(max_length=255, null=True, blank=True)
    ai_body = models.TextField(null=True, blank=True)
    related_market = models.CharField(max_length=127, choices=MarketType.choices)

    is_ready_to_be_announced = models.BooleanField()

    objects = MarketWatcherNotifManager()


class Meta:
    verbose_name = __("Market Watcher Notif")
    db_table = "fundamentalanalysis_marketwatchernotif"


class MarketWatcherNotifFeatureModel(BaseFeatureModel):
    class Meta:
        verbose_name = __("MarketWatcher Notif Feature")
        db_table = "fundamentalanalysis_marketwatchernotiffeature"


class MarketWatcherNotifSatisfyModel(TimeStampedModel, models.Model):
    feature = models.ForeignKey(
        MarketWatcherNotifFeatureModel, on_delete=models.CASCADE, related_name="marketwatchernotiffeature_set"
    )
    notif = models.ForeignKey(
        MarketWatcherNotifModel, on_delete=models.CASCADE, related_name="marketwatchernotiffeature_set"
    )
