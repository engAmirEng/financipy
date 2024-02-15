from django.contrib import admin

from financipy.core.models import SymbolModel


@admin.register(SymbolModel)
class SymbolAdmin(admin.ModelAdmin):
    pass
