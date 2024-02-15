from aiogram import Bot, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as __

from financipy.fundamental_analysis.models import MarketWatcherNotifProfileModel

from . import router
from .base import MenuCallback, MenuType

UserModel = get_user_model()


class NotificationType(models.TextChoices):
    MARKET_WATCHER = "market_watcher", __("market_watcher")


class NotificationsMenuCallback(CallbackData, prefix="notification"):
    notification_type: NotificationType


@router.callback_query(MenuCallback.filter(F.key == MenuType.notifications))
async def base_notifications_handler(
    query: CallbackQuery, callback_data: MenuCallback, bot: Bot, user: UserModel
) -> None:
    ikbuilder = InlineKeyboardBuilder()
    market_watcher_notif_feature_obj = await MarketWatcherNotifProfileModel.objects.get_for_user(user=user)
    ikbuilder.button(
        text=_("market watcher notifications")
        + "    | "
        + ("✅" if market_watcher_notif_feature_obj.is_active else "❌"),
        callback_data=NotificationsMenuCallback(notification_type=NotificationType.MARKET_WATCHER),
    )
    await query.message.edit_text(_("notifications"), reply_markup=ikbuilder.as_markup())
