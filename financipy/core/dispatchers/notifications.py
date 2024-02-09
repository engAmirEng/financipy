import asyncio
from typing import TYPE_CHECKING

from aiogram import Bot, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils import timezone

from ..utils.feature import make_feature_status_text

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from django.utils.translation import gettext as _

from ...fundamental_analysis.models import MarketWatcherNotifFeatureModel
from ..models.feature import BaseFeatureModel
from . import router
from .core import MenuCallback, MenuType


class NotificationsCallback(CallbackData, prefix="notification"):
    market_watcher_ai_boosted: bool


@router.callback_query(MenuCallback.filter(F.key == MenuType.notifications))
async def base_notifications_handler(
    query: CallbackQuery, callback_data: MenuCallback, bot: Bot, user: "AbstractUser"
) -> None:
    ikbuilder = InlineKeyboardBuilder()
    market_watcher_notif_feature_obj = await MarketWatcherNotifFeatureModel.objects.get_status_for_user(user)
    ikbuilder.button(
        text=make_feature_status_text(
            _("Market watcher notifications"),
            feature_type=MarketWatcherNotifFeatureModel,
            feature=market_watcher_notif_feature_obj,
        ),
        callback_data=NotificationsCallback(
            market_watcher_ai_boosted=not (market_watcher_notif_feature_obj.is_active)
        ),
    )
    await query.message.edit_text(_("Notifications"), reply_markup=ikbuilder.as_markup())


@router.callback_query(NotificationsCallback.filter())
async def notifications_handler(
    query: CallbackQuery, callback_data: NotificationsCallback, bot: Bot, user: "AbstractUser"
) -> None:
    now = timezone.now()
    market_watcher_notif_feature_obj = await MarketWatcherNotifFeatureModel.objects.get_last_for_user(user=user)

    ikbuilder = InlineKeyboardBuilder()
    if callback_data.market_watcher_ai_boosted:
        if not market_watcher_notif_feature_obj.is_active:
            if market_watcher_notif_feature_obj.is_active is None:
                market_watcher_notif_feature_obj = MarketWatcherNotifFeatureModel()
                market_watcher_notif_feature_obj.start = now
                market_watcher_notif_feature_obj.user = user
                market_watcher_notif_feature_obj.status = BaseFeatureModel.Status.ACTIVE
                await market_watcher_notif_feature_obj.asave()
                asyncio.create_task(query.answer(text=_("activated")))
    else:
        if market_watcher_notif_feature_obj.is_active:
            market_watcher_notif_feature_obj.status = BaseFeatureModel.Status.INACTIVE_BY_CHOICE
            await market_watcher_notif_feature_obj.asave()
            asyncio.create_task(query.answer(_("deactivated")))

    ikbuilder.button(
        text=make_feature_status_text(
            _("Market watcher notifications"),
            feature_type=MarketWatcherNotifFeatureModel,
            feature=market_watcher_notif_feature_obj,
        ),
        callback_data=NotificationsCallback(market_watcher_ai_boosted=not market_watcher_notif_feature_obj.is_active),
    )
    await query.message.edit_text(_("Notifications"), reply_markup=ikbuilder.as_markup())
