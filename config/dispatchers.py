from aiogram import Dispatcher, Router

from financipy.core.dispatchers import router as core_router
from financipy.fundamental_analysis.dispatchers import router as fundamental_analysis_router
from financipy.technical_analysis.dispatchers import router as technical_analysis_router
from financipy.users.dispatchers import complete_profile_handler
from financipy.users.dispatchers import router as users_router
from financipy.users.utils import HasCompleteProfileTFilter

dp = Dispatcher()

pre_router = Router(name="pre")
pre_router.message(~HasCompleteProfileTFilter())(complete_profile_handler)

dp.include_router(pre_router)
dp.include_router(core_router)
dp.include_router(technical_analysis_router)
dp.include_router(fundamental_analysis_router)
dp.include_router(users_router)
