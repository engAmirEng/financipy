from django.db import models
from django.utils.translation import gettext_lazy as __

from .managers import OHLCManager


class SymbolModel(models.Model):
    name = models.CharField(max_length=63, db_index=True, unique=True)

    class Meta:
        verbose_name = __("Symbol")
        db_table = "symbol"

    def __str__(self):
        return f"{str(self.id)} - {self.name}"


class OHLCModel(models.Model):
    objects = OHLCManager()

    symbol = models.ForeignKey(SymbolModel, on_delete=models.CASCADE, related_name="ohlc_set")
    created_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to="technical_analysis/ohlc")

    class Meta:
        verbose_name = __("OHLC")
        db_table = "ohlc"

    def __str__(self):
        return f"{str(self.id)} - {self.symbol.name}"
