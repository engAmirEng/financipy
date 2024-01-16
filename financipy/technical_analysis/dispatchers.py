import io

import mplfinance as mpf
import numpy as np
import pandas as pd
import talib

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.utils.translation import gettext as _

from financipy.core.dispatchers import MenuCallback, MenuType

router = Router(name="technical_analysis")


class TechnicalBuilderState(StatesGroup):
    symbol_name = State()
    date_after = State()


@router.callback_query(MenuCallback.filter(F.key == MenuType.technical_builder))
async def technical_builder_handler(
    query: CallbackQuery, callback_data: MenuCallback, state: FSMContext, bot: Bot
) -> None:
    await state.set_state(TechnicalBuilderState.symbol_name)
    await query.message.edit_text(_("enter the name"))


@router.message(TechnicalBuilderState.symbol_name)
async def process_name(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(symbol_name=message.text)
    await state.set_state(TechnicalBuilderState.date_after)
    await message.answer(_("enter the date"))


@router.message(TechnicalBuilderState.date_after)
async def process_date(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(date_after=message.text)
    data = await state.get_data()
    await state.clear()

    # df = pytse_client.download(symbols=data["symbol_name"], adjust=True)
    df = pd.read_csv("media/aa.csv")
    df.index = pd.DatetimeIndex(df["date"])

    date_after = data["date_after"]
    df = df.loc[date_after::]
    df["hammer"] = talib.CDLHAMMER(df["open"], df["high"], df["low"], df["close"])
    hammer_df = pd.DataFrame(index=df.index)
    hammer_df["close"] = np.where(df["hammer"] > 0, df["close"], np.nan)
    hammer_df["my"] = hammer_df["close"] + 50
    hammer_plt = mpf.make_addplot(hammer_df["my"], scatter=True, markersize=20, color="b", secondary_y=False)
    buf = io.BytesIO()
    mpf.plot(df, type="candle", style="yahoo", addplot=[hammer_plt], volume=True, savefig=buf)
    buf.seek(0)

    builder = InlineKeyboardBuilder()
    builder.button(text=_("add hammer"), callback_data=MenuCallback(key=MenuType.technical_builder))
    builder.button(text=_("add trend line"), callback_data=MenuCallback(key=MenuType.technical_builder))
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=BufferedInputFile(file=buf.read(), filename="fdfd"),
        caption=_("here you are"),
        reply_markup=builder.as_markup(),
    )
