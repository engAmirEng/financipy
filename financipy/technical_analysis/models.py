from django.db import models
from django.utils.translation import gettext_lazy as __

from financipy.core.models import SymbolModel
from financipy.utils.models import TimeStampedModel

from .managers import OHLCManager


class OHLCModel(TimeStampedModel, models.Model):
    objects = OHLCManager()

    symbol = models.ForeignKey(SymbolModel, on_delete=models.CASCADE, related_name="ohlc_set")
    created_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to="technical_analysis/ohlc")

    class Meta:
        verbose_name = __("OHLC")
        db_table = "technicalanalysis_ohlc"

    def __str__(self):
        return f"{str(self.id)} - {self.symbol.name}"
