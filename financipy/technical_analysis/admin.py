from django.contrib import admin

from .models import OHLCModel


@admin.register(OHLCModel)
class OHLCAdmin(admin.ModelAdmin):
    pass
