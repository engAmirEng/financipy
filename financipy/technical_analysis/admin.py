from django.contrib import admin

from .models import OHLCModel, SymbolModel


@admin.register(SymbolModel)
class SymbolAdmin(admin.ModelAdmin):
    pass


@admin.register(OHLCModel)
class OHLCAdmin(admin.ModelAdmin):
    pass
