import random
import string

from django.contrib.auth.models import UserManager as BaseUserManager


class UserManager(BaseUserManager):
    async def make_username(self, base=None, length=15) -> str:
        base = base or ""
        length -= len(base)
        characters = string.ascii_letters + string.digits + string.punctuation
        while True:
            username = base + "".join(random.choice(characters) for _ in range(length))
            if not self.first(username=username).exists():
                return username
