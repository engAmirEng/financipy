from django.contrib import admin

from .models import MarketWatcherNotifModel, MarketWatcherNotifProfileModel, MarketWatcherNotifSatisfyModel


@admin.register(MarketWatcherNotifModel)
class MarketWatcherNotifAdmin(admin.ModelAdmin):
    pass


@admin.register(MarketWatcherNotifProfileModel)
class MarketWatcherNotifProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(MarketWatcherNotifSatisfyModel)
class MarketWatcherNotifSatisfyAdmin(admin.ModelAdmin):
    pass
