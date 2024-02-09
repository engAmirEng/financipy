from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from django.utils.translation import gettext as _

from financipy.core.dispatchers.notifications import NotificationsCallback, NotificationType

router = Router(name="fundamental_analysis")


@router.callback_query(NotificationsCallback.filter(F.key == NotificationType.market_watcher_ai_boosted))
async def start_technical_builder_handler(
    query: CallbackQuery, callback_data: NotificationsCallback, state: FSMContext, bot: Bot
) -> None:
    await query.message.edit_text(_("enter the name"))
