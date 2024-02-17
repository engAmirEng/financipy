import json
from typing import Optional, Union

from aiogram import Bot, F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from financipy.core.dispatchers.notifications import NotificationsMenuCallback, NotificationType

from .models import MarketWatcherNotifModel, MarketWatcherNotifProfileModel

router = Router(name="fundamental_analysis")

UserModel = get_user_model()


class MarketWatcherNotificationCallback(CallbackData, prefix="notification"):
    activate: Optional[bool] = None
    ai_boosted: Optional[bool] = None


@router.callback_query(NotificationsMenuCallback.filter(F.notification_type == NotificationType.MARKET_WATCHER))
@router.callback_query(MarketWatcherNotificationCallback.filter())
async def market_watcher_notifications_handler(
    query: CallbackQuery,
    callback_data: Union[NotificationsMenuCallback, MarketWatcherNotificationCallback],
    bot: Bot,
    user: UserModel,
) -> None:
    market_watcher_notif_feature_obj = await MarketWatcherNotifProfileModel.objects.aget(user=user)
    if isinstance(callback_data, NotificationsMenuCallback):
        callback_data = MarketWatcherNotificationCallback()

    ikbuilder = InlineKeyboardBuilder()
    if callback_data.activate:
        if not market_watcher_notif_feature_obj.is_active:
            market_watcher_notif_feature_obj.status = market_watcher_notif_feature_obj.Status.ACTIVE
            await market_watcher_notif_feature_obj.asave()
            await query.answer(text=_("activated"))
    elif callback_data.activate is None:
        pass
    else:
        if market_watcher_notif_feature_obj.is_active:
            market_watcher_notif_feature_obj.status = market_watcher_notif_feature_obj.Status.INACTIVE
            await market_watcher_notif_feature_obj.asave()
            await query.answer(_("deactivated"))
    if callback_data.ai_boosted:
        if not market_watcher_notif_feature_obj.ai_boosted:
            market_watcher_notif_feature_obj.ai_boosted = True
            await market_watcher_notif_feature_obj.asave()
            await query.answer(text=_("ai boost activated"))
    elif callback_data.ai_boosted is None:
        pass
    else:
        if market_watcher_notif_feature_obj.ai_boosted:
            market_watcher_notif_feature_obj.ai_boosted = False
            await market_watcher_notif_feature_obj.asave()
            await query.answer(_("ai boost deactivated"))

    ikbuilder.button(
        text=_("status") + "    | " + ("✅" if market_watcher_notif_feature_obj.is_active else "❌"),
        callback_data=MarketWatcherNotificationCallback(activate=not market_watcher_notif_feature_obj.is_active),
    )
    if market_watcher_notif_feature_obj.is_active:
        ikbuilder.button(
            text=_("ai boost") + "    | " + ("✅" if market_watcher_notif_feature_obj.ai_boosted else "❌"),
            callback_data=MarketWatcherNotificationCallback(
                ai_boosted=not market_watcher_notif_feature_obj.ai_boosted,
            ),
        )
    await query.message.edit_text(_("market watcher notifications"), reply_markup=ikbuilder.as_markup())


class SeeMarketWatcherNotificationModeCallback(CallbackData, prefix="notification"):
    json_notification_ids: str
    ai_boosted: bool


@router.callback_query(SeeMarketWatcherNotificationModeCallback.filter())
async def see_market_watcher_notification_mode_handler(
    query: CallbackQuery,
    callback_data: SeeMarketWatcherNotificationModeCallback,
    bot: Bot,
    user: UserModel,
) -> None:
    notification_ids: list[int] = json.loads(callback_data.json_notification_ids)
    mwns = MarketWatcherNotifModel.objects.filter(id__in=notification_ids).select_related("related_symbol")
    body = ""
    async for mwn in mwns:
        if mwn.related_symbol.name:
            body += f"#{mwn.related_symbol.name}" + "\n"
        if callback_data.ai_boosted:
            if not mwn.ai_boosted_yet:
                body += _("not available yet")
                body += "\n\n\n"
            else:
                body += mwn.original_title + "\n"
                body += mwn.ai_body + "\n"
                body += "\n\n\n"
        else:
            body += mwn.original_title + "\n"
            body += mwn.original_body + "\n"
            body += "\n\n\n"
    ikbuilder = InlineKeyboardBuilder()
    ikbuilder.button(
        text=_("see in original mode") if callback_data.ai_boosted else _("see in ai boosted mode"),
        callback_data=SeeMarketWatcherNotificationModeCallback(
            json_notification_ids=json.dumps([i.id for i in mwns]), ai_boosted=not callback_data.ai_boosted
        ),
    )
    await query.message.edit_text(body, reply_markup=ikbuilder.as_markup())
