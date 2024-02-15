from enum import Enum

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils.translation import gettext as _


class MenuType(str, Enum):
    technical_builder = "technical_builder"
    notifications = "notifications"


class MenuCallback(CallbackData, prefix="menu"):
    key: MenuType


router = Router(name="core")


@router.message(CommandStart())
async def command_start_handler(message: Message, *args, **kwargs) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("technical builder"), callback_data=MenuCallback(key=MenuType.technical_builder))
    builder.button(text=_("manage Notifications"), callback_data=MenuCallback(key=MenuType.notifications))
    await message.answer("menu", reply_markup=builder.as_markup())
