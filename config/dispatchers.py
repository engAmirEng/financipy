from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")
