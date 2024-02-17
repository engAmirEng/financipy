import random
import string
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models

if TYPE_CHECKING:
    from .models import UserProfileModel

    UserModel = get_user_model()


class UserManager(BaseUserManager):
    async def make_username(self, base=None, length=15) -> str:
        base = base or ""
        length -= len(base)
        characters = string.ascii_letters + string.digits
        while True:
            username = base + "".join(random.choice(characters) for _ in range(length))
            if not await self.filter(username=username).aexists():
                return username


class UserProfileManager(models.Manager):
    async def create_from_initial_ask(self, user: "UserModel", language: str, calendar: str, timezone: str):
        obj: "UserProfileModel" = self.model()
        obj.user = user
        obj.preferred_language = language
        obj.latest_language = language
        obj.preferred_calendar = calendar
        obj.preferred_timezone = timezone
        await obj.asave()
        return obj
