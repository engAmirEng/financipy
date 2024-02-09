from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async

from django.contrib.auth import get_user_model
from django.db import models, transaction

if TYPE_CHECKING:
    from aiogram.types import User as TUser

    from .models import TelegramUserProfileModel

UserModel = get_user_model()


class TelegramUserProfileManager(models.Manager):
    @transaction.atomic
    async def auto_new_from_user_tevent(self, tuser: "TUser") -> "TelegramUserProfileModel":
        username = await UserModel.objects.make_username(base=tuser.username)
        user = await sync_to_async(UserModel.objects.create_user)(username=username)
        obj: "TelegramUserProfileModel" = self.model()
        obj.suer = user
        obj.user_oid = tuser.id
        obj.username = tuser.username
        obj.is_default = True
        await obj.asave()
        return obj
