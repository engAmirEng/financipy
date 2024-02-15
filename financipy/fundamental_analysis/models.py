from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as __

from financipy.core.models import MarketType
from financipy.fundamental_analysis.managers import MarketWatcherNotifManager, MarketWatcherNotifProfileManager
from financipy.utils.models import TimeStampedModel


class MarketWatcherNotifModel(TimeStampedModel, models.Model):
    original_title = models.CharField(max_length=255)
    original_body = models.TextField()
    publish_time = models.DateTimeField()
    ai_body = models.TextField(null=True, blank=True)
    related_market = models.CharField(max_length=127, choices=MarketType.choices)
    related_symbol = models.ForeignKey(
        "core.SymbolModel", on_delete=models.CASCADE, related_name="marketwatchernotif_set", null=True, blank=True
    )

    objects = MarketWatcherNotifManager()

    class Meta:
        verbose_name = __("Market Watcher Notif")
        db_table = "fundamentalanalysis_marketwatchernotif"

    @property
    def ai_boosted_yet(self):
        return self.ai_body


class MarketWatcherNotifProfileModel(TimeStampedModel, models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", __("active")
        INACTIVE = "inactive", __("inactive")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketwatchernotifprofile"
    )
    status = models.CharField(choices=Status.choices)
    ai_boosted = models.BooleanField()

    objects = MarketWatcherNotifProfileManager()

    class Meta:
        verbose_name = __("MarketWatcher Notif Profile")
        db_table = "fundamentalanalysis_marketwatchernotifprofile"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


class MarketWatcherNotifSatisfyModel(TimeStampedModel, models.Model):
    profile = models.ForeignKey(
        MarketWatcherNotifProfileModel, on_delete=models.CASCADE, related_name="marketwatchernotifsatisfy_set"
    )
    notif = models.ForeignKey(
        MarketWatcherNotifModel, on_delete=models.CASCADE, related_name="marketwatchernotifsatisfy_set"
    )
    ai_boosted = models.BooleanField()

    class Meta:
        verbose_name = __("Market Watcher Notif Satisfy")
        db_table = "fundamentalanalysis__marketwatchernotifsatisfy"
