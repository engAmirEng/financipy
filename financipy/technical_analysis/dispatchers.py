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

from .models import OHLCModel
from .strategy_utils.hh_hl_lh_ll import get_tline_output, getHigherHighs, getHigherLows, getLowerHighs, getLowerLows

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

    df = await OHLCModel.objects.get_ensured_df(symbol_name)
    df = df[df["Date"] > date_after]
    df = df.reset_index()

    buf = io.BytesIO()
    df.index = df["Date"]
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
    df = await OHLCModel.objects.get_ensured_df(callback_data.symbol_name)
    df = df[df["Date"] > callback_data.date_after]
    df = df.reset_index()

    addplot = []
    tlines = []

    ikbuilder = InlineKeyboardBuilder()

    if callback_data.hammer:
        df["Hammer"] = talib.CDLHAMMER(df["Open"], df["High"], df["Low"], df["Close"])
        hammer_df = pd.DataFrame(index=df.index)
        hammer_df["Close"] = np.where(df["Hammer"] > 0, df["Close"], np.nan)
        hammer_df["My"] = hammer_df["Close"] + 50
        hammer_plt = mpf.make_addplot(hammer_df["My"], scatter=True, markersize=20, color="b", secondary_y=False)
        addplot.append(hammer_plt)

        local_callback_data = deepcopy(callback_data)
        local_callback_data.hammer = False
        ikbuilder.button(text=_("remove hammer"), callback_data=local_callback_data)
    else:
        local_callback_data = deepcopy(callback_data)
        local_callback_data.hammer = True
        ikbuilder.button(text=_("add hammer"), callback_data=local_callback_data)

    if callback_data.trend:
        close = df["Close"].values
        order = 5
        K = 2
        hh = getHigherHighs(close, order, K)
        hl = getHigherLows(close, order, K)
        ll = getLowerLows(close, order, K)
        lh = getLowerHighs(close, order, K)

        hh_tlines = get_tline_output(hh, df)
        tlines.append({"tlines": hh_tlines, "colors": "b"})
        hl_tlines = get_tline_output(hl, df)
        tlines.append({"tlines": hl_tlines, "colors": "b"})
        ll_tlines = get_tline_output(ll, df)
        tlines.append({"tlines": ll_tlines, "colors": "r"})
        lh_tlines = get_tline_output(lh, df)
        tlines.append({"tlines": lh_tlines, "colors": "r"})

        local_callback_data = TechnicalBuilderCallback(**callback_data.model_dump())
        local_callback_data.trend = False
        ikbuilder.button(text=_("remove trend line"), callback_data=local_callback_data)
    else:
        local_callback_data = TechnicalBuilderCallback(**callback_data.model_dump())
        local_callback_data.trend = True
        ikbuilder.button(text=_("add tren line"), callback_data=local_callback_data)
    buf = io.BytesIO()
    df.index = df["Date"]
    mpf.plot(df, type="candle", style="yahoo", addplot=addplot, tlines=tlines, volume=True, savefig=buf)
    buf.seek(0)
    figure = buf.read()

    await query.message.edit_media(
        media=InputMediaPhoto(media=BufferedInputFile(file=figure, filename="fdfd")),
        reply_markup=ikbuilder.as_markup(),
    )
