from django.db import models
from django.utils.translation import gettext_lazy as __

from financipy.utils.models import TimeStampedModel


class MarketType(models.TextChoices):
    tehran_stock_exchange = "tehran_stock_exchange", __("Tehran Stock Exchange")


class SymbolModel(TimeStampedModel, models.Model):
    name = models.CharField(max_length=63, db_index=True, unique=True)
    market = models.CharField(max_length=127, choices=MarketType.choices)

    class Meta:
        verbose_name = __("Symbol")
        db_table = "core_symbol"

    def __str__(self):
        return f"{str(self.id)} - {self.name}"
