from aiogram import Dispatcher

from financipy.core.dispatchers import router as core_router
from financipy.fundamental_analysis.dispatchers import router as fundamental_analysis_router
from financipy.technical_analysis.dispatchers import router as technical_analysis_router

dp = Dispatcher()
dp.include_router(core_router)
dp.include_router(technical_analysis_router)
dp.include_router(fundamental_analysis_router)
