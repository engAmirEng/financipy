from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as __

from financipy.utils.models import TimeStampedModel

from ..managers.feature import BaseFeatureManager


class BaseFeatureModel(TimeStampedModel, models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", __("active")
        INACTIVE_BY_CHOICE = "inactive_by_choice", __("inactive by choice")

    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="base")
    status = models.CharField()

    objects = BaseFeatureManager()

    class Meta:
        verbose_name = __("Base Feature")
        db_table = "core_basefeature"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE
