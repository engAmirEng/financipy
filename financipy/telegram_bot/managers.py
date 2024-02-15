from typing import TYPE_CHECKING

from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model
from django.db import models, transaction

if TYPE_CHECKING:
    from aiogram.types import User as TUser

    from .models import TelegramUserProfileModel

UserModel = get_user_model()


class TelegramUserProfileManager(models.Manager):
    @transaction.atomic
    def auto_new_from_user_tevent(self, tuser: "TUser") -> "TelegramUserProfileModel":
        username = async_to_sync(UserModel.objects.make_username)(base=tuser.username)
        user = UserModel.objects.create_user(username=username)
        obj: "TelegramUserProfileModel" = self.model()
        obj.user = user
        obj.user_oid = tuser.id
        obj.username = tuser.username
        obj.is_default = True
        obj.save()
        return obj
