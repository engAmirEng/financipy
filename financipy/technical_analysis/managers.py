import pandas as pd
import pytse_client
from asgiref.sync import sync_to_async

from django.core.files.base import ContentFile
from django.db import models

from .utils import InvalidSymbol, ohlc_df_normalize


class OHLCManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("symbol")

    async def get_ensured_df(self, symbol_name: str) -> pd.DataFrame:
        """
        :raises InvalidSymbol
        """
        try:
            ohlc_obj = await self.aget(symbol__name=symbol_name)
            df = pd.read_csv(ohlc_obj.csv_file)
        except self.model.DoesNotExist:
            from financipy.technical_analysis.models import SymbolModel

            try:
                df_dict = await sync_to_async(pytse_client.download)(symbols=symbol_name, adjust=True)
            except Exception as e:
                if "Cannot find symbol" in str(e):
                    raise InvalidSymbol(str(e))
                raise e
            raw_df = df_dict[symbol_name]
            df = ohlc_df_normalize(raw_df)

            csv_res = df.to_csv()
            ohlc_obj = self.model()
            symbol, is_created = await SymbolModel.objects.aget_or_create(name=symbol_name)
            ohlc_obj.symbol = symbol
            await sync_to_async(ohlc_obj.csv_file.save)(f"{symbol_name}.csv", content=ContentFile(csv_res), save=True)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
