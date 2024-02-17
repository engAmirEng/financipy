from aiogram import Bot, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.contrib.auth import get_user_model
from django.utils import translation
from django.utils.translation import gettext as _

from financipy.core.dispatchers import MenuCallback
from financipy.users.models import UserProfileModel

router = Router(name="users")

UserModel = get_user_model()


class ProfileState(StatesGroup):
    language = State()
    timezone = State()
    calendar = State()


class LanguageCallback(CallbackData, prefix="profile_lang"):
    language: str


class TimeZoneCallback(CallbackData, prefix="profile_timezone"):
    timezone: str


class CalendarCallback(CallbackData, prefix="prodfile_calendar"):
    calendar: str


async def complete_profile_handler(message: Message, *args, **kwargs) -> None:
    text_message = (
        "پیش از استفاده ابتدا پروفایلتان را کامل کنید، این تنظیمات بعدا قابل تفییر هستند"
        "before start using the bot, please complete your profile, these settings can be changed later"
        "\n\n\n"
        "زبان خود را انتخاب کنید | select your language"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="fa | Persian | پارسی", callback_data=LanguageCallback(language="fa"))
    builder.button(text="en | English | انگلیسی", callback_data=LanguageCallback(language="en"))
    builder.button(text="ar | Arabic | عربی", callback_data=LanguageCallback(language="ar"))
    builder.adjust(1, 1, 1)
    await message.answer(text_message, reply_markup=builder.as_markup())


@router.callback_query(LanguageCallback.filter())
async def complete_profile_save_lang_handler(
    query: CallbackQuery, callback_data: MenuCallback, bot: Bot, state: FSMContext, user: UserModel
) -> None:
    await state.update_data(language=LanguageCallback.unpack(query.data).language)
    state_data = await state.get_data()
    translation.activate(state_data["language"])
    text_message = _("which time zone are you in?")
    builder = InlineKeyboardBuilder()
    builder.button(text=_("asia") + "/" + _("tehran"), callback_data=TimeZoneCallback(timezone="Asia/Tehran"))
    await query.message.edit_text(text_message, reply_markup=builder.as_markup())


@router.callback_query(TimeZoneCallback.filter())
async def complete_profile_save_timezone_handler(
    query: CallbackQuery, callback_data: MenuCallback, bot: Bot, state: FSMContext, user: UserModel
) -> None:
    await state.update_data(timezone=TimeZoneCallback.unpack(query.data).timezone)
    state_data = await state.get_data()
    translation.activate(state_data["language"])
    text_message = _("which calendar type do you prefer?")
    builder = InlineKeyboardBuilder()
    for i in UserProfileModel.Calendar.choices:
        builder.button(text=_(i[1]), callback_data=CalendarCallback(calendar=i[0]))
    await query.message.edit_text(text_message, reply_markup=builder.as_markup())


@router.callback_query(CalendarCallback.filter())
async def complete_profile_save_calendar_handler(
    query: CallbackQuery, callback_data: MenuCallback, bot: Bot, state: FSMContext, user: UserModel
) -> None:
    await state.update_data(calendar=CalendarCallback.unpack(query.data).calendar)
    state_data = await state.get_data()
    translation.activate(state_data["language"])
    await UserProfileModel.objects.create_from_initial_ask(
        user, language=state_data["language"], calendar=state_data["calendar"], timezone=state_data["timezone"]
    )
    await query.message.edit_text(_("successfully saved"))
