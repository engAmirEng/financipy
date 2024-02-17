from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from asgiref.sync import sync_to_async

from aiogram import BaseMiddleware
from aiogram.types import Chat, TelegramObject, User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone, translation

from financipy.telegram_bot.models import TelegramUserProfileModel

if TYPE_CHECKING:
    from financipy.users.models import UserProfileModel

UserModel = get_user_model()


class AuthenticationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event_chat: Chat = data["event_chat"]
        event_from_user: User = data["event_from_user"]
        try:
            telegram_user_profile_obj = await TelegramUserProfileModel.objects.select_related("user").aget(
                user_oid=event_from_user.id
            )
            if not telegram_user_profile_obj.is_default:
                raise NotImplementedError
        except TelegramUserProfileModel.DoesNotExist:
            if event_chat.type == "private":
                telegram_user_profile_obj = await sync_to_async(
                    TelegramUserProfileModel.objects.auto_new_from_user_tevent
                )(event_from_user)
            else:
                telegram_user_profile_obj = None

        data.update(user=telegram_user_profile_obj.user if telegram_user_profile_obj else AnonymousUser())
        return await handler(event, data)


class FullLocaleMiddleware(BaseMiddleware):
    """AuthenticationMiddleware should be before this"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event_chat: Chat = data["event_chat"]
        event_from_user: User = data["event_from_user"]
        user: UserModel = data["user"]
        if event_chat.type == "private":
            try:
                user_profile: "UserProfileModel" = await sync_to_async(lambda: user.userprofile)()
            except UserModel.userprofile.RelatedObjectDoesNotExist:
                translation.activate(event_from_user.language_code or settings.LANGUAGE_CODE)
            else:
                timezone.activate(ZoneInfo(user_profile.preferred_timezone))
                language = user_profile.preferred_language or event_from_user.language_code
                translation.activate(language)
                if user_profile.latest_language != language:
                    user_profile.latest_language = language
                    await user_profile.asave()
        response = await handler(event, data)
        timezone.deactivate()
        return response
