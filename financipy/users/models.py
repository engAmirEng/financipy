from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from financipy.users.managers import UserManager
from financipy.utils.models import TimeStampedModel

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

    _t_profile: "TelegramUserProfileModel"

    @property
    async def t_profile(self):
        """
        :raises TelegramUserProfileModel.DoesNotExist
        """
        if self._t_profile is None:
            t_profile = await self.telegramuserprofile_set.aget(is_default=True)
            self._t_profile = t_profile
        return self._t_profile
