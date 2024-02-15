from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as __

from financipy.telegram_bot.managers import TelegramUserProfileManager
from financipy.utils.models import TimeStampedModel


class TelegramUserProfileModel(TimeStampedModel, models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegramuserprofile_set"
    )
    user_oid = models.BigIntegerField(unique=True, db_index=True)
    is_default = models.BooleanField(default=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    objects = TelegramUserProfileManager()

    class Meta:
        verbose_name = __("Telegram User Profile")
        db_table = "telegrambot_telegramuserprofile"
        constraints = [
            models.UniqueConstraint(
                fields=("user",), condition=Q(is_default=True), name="only_one_default_telegram_profile_per_user"
            )
        ]
