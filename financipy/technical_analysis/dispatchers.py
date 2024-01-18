import io
from copy import deepcopy

import mplfinance as mpf
import numpy as np
import pandas as pd
import talib

from aiogram import Bot, F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils.translation import gettext as _

from financipy.core.dispatchers import MenuCallback, MenuType

router = Router(name="technical_analysis")


class TechnicalBuilderState(StatesGroup):
    symbol_name = State()
    date_after = State()


@router.callback_query(MenuCallback.filter(F.key == MenuType.technical_builder))
async def start_technical_builder_handler(
    query: CallbackQuery, callback_data: MenuCallback, state: FSMContext, bot: Bot
) -> None:
    await state.set_state(TechnicalBuilderState.symbol_name)
    await query.message.edit_text(_("enter the name"))


@router.message(TechnicalBuilderState.symbol_name)
async def process_name_technical_builder_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(symbol_name=message.text)
    await state.set_state(TechnicalBuilderState.date_after)
    await message.answer(_("enter the date"))


@router.message(TechnicalBuilderState.date_after)
async def process_date_technical_builder_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(date_after=message.text)
    data = await state.get_data()
    await state.clear()
    symbol_name = data["symbol_name"]
    date_after = data["date_after"]

    df = get_df(symbol_name=symbol_name, date_after=date_after)
    buf = io.BytesIO()
    mpf.plot(df, type="candle", style="yahoo", volume=True, savefig=buf)
    buf.seek(0)
    figure = buf.read()

    ikbuilder = InlineKeyboardBuilder()
    ikbuilder.button(
        text=_("add hammer"),
        callback_data=TechnicalBuilderCallback(
            symbol_name=symbol_name, date_after=date_after, hammer=True, trend=False
        ),
    )
    ikbuilder.button(
        text=_("add trend line"),
        callback_data=TechnicalBuilderCallback(
            symbol_name=symbol_name, date_after=date_after, hammer=False, trend=True
        ),
    )
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=BufferedInputFile(file=figure, filename="fdfd"),
        caption=_("here you are"),
        reply_markup=ikbuilder.as_markup(),
    )


class TechnicalBuilderCallback(CallbackData, prefix="technical_builder"):
    symbol_name: str
    date_after: str

    hammer: bool
    trend: bool


@router.callback_query(TechnicalBuilderCallback.filter())
async def process_main_technical_builder_handler(
    query: CallbackQuery, callback_data: TechnicalBuilderCallback, state: FSMContext, bot: Bot
):
    df = get_df(symbol_name=callback_data.symbol_name, date_after=callback_data.date_after)
    addplot = []
    ikbuilder = InlineKeyboardBuilder()

    if callback_data.hammer:
        df["hammer"] = talib.CDLHAMMER(df["open"], df["high"], df["low"], df["close"])
        hammer_df = pd.DataFrame(index=df.index)
        hammer_df["close"] = np.where(df["hammer"] > 0, df["close"], np.nan)
        hammer_df["my"] = hammer_df["close"] + 50
        hammer_plt = mpf.make_addplot(hammer_df["my"], scatter=True, markersize=20, color="b", secondary_y=False)
        addplot.append(hammer_plt)

        local_callback_data = deepcopy(callback_data)
        local_callback_data.hammer = False
        ikbuilder.button(text=_("remove hammer"), callback_data=local_callback_data)
    else:
        local_callback_data = deepcopy(callback_data)
        local_callback_data.hammer = True
        ikbuilder.button(text=_("add hammer"), callback_data=local_callback_data)

    if callback_data.trend:
        local_callback_data = deepcopy(callback_data)
        local_callback_data.hammer = False
        ikbuilder.button(text=_("remove trend line"), callback_data=local_callback_data)
    else:
        local_callback_data = deepcopy(callback_data)
        local_callback_data.hammer = True
        ikbuilder.button(text=_("add tren line"), callback_data=local_callback_data)
    buf = io.BytesIO()
    mpf.plot(df, type="candle", style="yahoo", addplot=addplot, volume=True, savefig=buf)
    buf.seek(0)
    figure = buf.read()

    await query.message.edit_media(
        media=InputMediaPhoto(media=BufferedInputFile(file=figure, filename="fdfd")),
        reply_markup=ikbuilder.as_markup(),
    )


def get_df(symbol_name: str, date_after) -> pd.DataFrame:
    # df = pytse_client.download(symbols=symbol_name, adjust=True)
    df = pd.read_csv("media/aa.csv")
    df.index = pd.DatetimeIndex(df["date"])

    df = df.loc[date_after::]
    return df
