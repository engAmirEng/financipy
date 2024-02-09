from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from ..models import BaseFeatureModel


class BaseFeatureQuerySet(models.QuerySet):
    def actives(self):
        now = timezone.now()

        return self.filter(Q(status=self.model.Status.ACTIVE, start__lt=now), Q(end_isnull=True) | Q(end__gt=now))


class BaseFeatureManager(models.Manager):
    def get_queryset(self):
        return BaseFeatureQuerySet(model=self.model, using=self._db, hints=self._hints)

    async def get_last_for_user(self, user: "AbstractUser") -> "BaseFeatureModel":
        now = timezone.now()
        last_feature = await self.filter(start__lt=now, user=user).order_by("-start").afirst()
        if last_feature is None:
            last_feature = self.model()
        return last_feature
