import json
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import jdatetime
import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from celery import shared_task

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import MarketWatcherNotifModel, MarketWatcherNotifProfileModel, MarketWatcherNotifSatisfyModel

if TYPE_CHECKING:
    from .types import TSETMCWatcherNotificationDataDict


@shared_task
def tsetmc_market_watcher_notifs_watcher():
    TSETMC_BASE_ADDR = "https://old.tsetmc.com"
    now = timezone.localtime(timezone.now(), timezone=ZoneInfo("Asia/Tehran"))
    tsetmc_date = jdatetime.datetime.fromgregorian(datetime=now).strftime("%Y-%m-%d")

    response = requests.get(
        f"{TSETMC_BASE_ADDR}/Loader.aspx?ParTree=151313&Flow=0&Lval18AFC=&DevenPersian={tsetmc_date}"
    )
    soup = BeautifulSoup(response.text, "html.parser")
    messages: list["TSETMCWatcherNotificationDataDict"] = []
    for i, v in enumerate(soup.select_one(".table1 tbody").select("tr")):
        if i % 2 == 0:
            new_record = {"title": v.select("th")[0].getText().strip()}
            time = jdatetime.datetime.strptime(
                v.select("th")[1].getText().strip(), format="%y/%m/%d %H:%M"
            ).togregorian()
            time = time.replace(tzinfo=ZoneInfo("Asia/Tehran"))
            new_record["time"] = time
            messages.append(new_record)
        else:
            messages[-1]["body"] = v.select_one("td").getText().strip()

    today_gatered_notifs_qs = MarketWatcherNotifModel.objects.filter(publish_time__date=now.date())

    market_watcher_notifs_title = [i.original_title for i in today_gatered_notifs_qs.only("original_title")]
    created_ids = []
    for message in messages:
        if message["title"] not in market_watcher_notifs_title:
            obj = MarketWatcherNotifModel.objects.new_from_tsetmc(message)
            created_ids.append(obj.pk)
    return {"total_fetched": len(messages), "created_ids": created_ids}


@shared_task
def market_watcher_notif_sender():
    session = AiohttpSession(proxy=settings.TELEGRAM_PROXY)
    bot = Bot(settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)

    now = timezone.now()
    candidate_mwns = MarketWatcherNotifModel.objects.filter(
        publish_time__gt=now - settings.MARKET_WATCHER_NOTIF_WINDOW
    )
    chat_count = 0
    for profile in MarketWatcherNotifProfileModel.objects.all().actives():
        mwns = candidate_mwns.exclude(marketwatchernotifsatisfy_set__profile=profile)
        if len(mwns) == 0:
            continue

        def satisfy(profile: MarketWatcherNotifProfileModel, mwns: QuerySet[MarketWatcherNotifModel]):
            from financipy.fundamental_analysis.dispatchers import SeeMarketWatcherNotificationModeCallback

            body = ""
            market_watcher_notif_satisfy_objs = []
            for mwn in mwns:
                if profile.ai_boosted and not mwn.ai_boosted_yet:
                    continue
                body += f"#{mwn.related_symbol.name}" + "\n"
                body += mwn.original_title + "\n"
                body += mwn.original_body + "\n"
                body += "\n\n\n"

                market_watcher_notif_satisfy_obj = MarketWatcherNotifSatisfyModel(
                    profile=profile, notif=mwn, ai_boosted=profile.ai_boosted
                )
                market_watcher_notif_satisfy_objs.append(market_watcher_notif_satisfy_obj)
            if not body:
                return
            ikbuilder = InlineKeyboardBuilder()
            ikbuilder.button(
                text=_("see in original mode") if profile.ai_boosted else _("see in ai boosted mode"),
                callback_data=SeeMarketWatcherNotificationModeCallback(
                    json_notification_ids=json.dumps([i.id for i in mwns]), ai_boosted=not profile.ai_boosted
                ),
            )
            async_to_sync(bot.send_message)(
                chat_id=profile.user.st_profile.user_oid, text=body, reply_markup=ikbuilder.as_markup()
            )
            MarketWatcherNotifSatisfyModel.objects.bulk_create(market_watcher_notif_satisfy_objs)

        satisfy(profile=profile, mwns=mwns)
        chat_count += 1
    return {"chat_count": chat_count}
