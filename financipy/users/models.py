from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as __

from financipy.users.managers import UserManager
from financipy.utils.models import TimeStampedModel
from financipy.utils.validators import validate_zoneinfo

if TYPE_CHECKING:
    from financipy.telegram_bot.models import TelegramUserProfileModel


class User(AbstractUser, TimeStampedModel):
    """
    Default custom user model for financipy.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    objects = UserManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._t_profile: Optional["TelegramUserProfileModel"] = None

    @property
    async def t_profile(self) -> "TelegramUserProfileModel":
        """
        :raises TelegramUserProfileModel.DoesNotExist
        """
        if self._t_profile is None:
            t_profile = await self.telegramuserprofile_set.aget(is_default=True)
            self._t_profile = t_profile
        return self._t_profile

    @property
    def st_profile(self) -> "TelegramUserProfileModel":
        """
        sync version of t_profile
        """
        if self._t_profile is None:
            t_profile = self.telegramuserprofile_set.get(is_default=True)
            self._t_profile = t_profile
        return self._t_profile


class UserProfileModel(TimeStampedModel, models.Model):
    class Calendar(models.TextChoices):
        GREGORIAN = "gregorian", __("gregorian")
        SOLAR_HIJRI = "solar_hijri", __("solar hijri")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userprofile", primary_key=True
    )

    preferred_language = models.CharField(max_length=3, choices=settings.LANGUAGES, null=True, blank=True)
    latest_language = models.CharField(max_length=3, choices=settings.LANGUAGES)
    preferred_timezone = models.CharField(max_length=15, validators=[validate_zoneinfo])
    preferred_calendar = models.CharField(max_length=15, choices=Calendar.choices)

    class Meta:
        verbose_name = __("User Profile")
        db_table = "users_userprofile"
