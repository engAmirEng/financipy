from asgiref.sync import sync_to_async

from aiogram.filters import Filter
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class HasCompleteProfileTFilter(Filter):
    async def __call__(self, *args, **kwargs) -> bool:
        user = kwargs.pop("user")
        try:
            await sync_to_async(lambda: user.userprofile)()
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            return False
        else:
            return True
