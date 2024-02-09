import asyncio
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import jdatetime
import requests
from bs4 import BeautifulSoup
from celery import shared_task

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from .models import MarketWatcherNotifFeatureModel, MarketWatcherNotifModel, MarketWatcherNotifSatisfyModel

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
    tasks = []
    async for feature in MarketWatcherNotifFeatureModel.objects.all().actives():
        mwns = candidate_mwns.exclude(marketwatchernotiffeature_set__feature=feature)

        async def satisfy(feature: MarketWatcherNotifFeatureModel, mwns: QuerySet[MarketWatcherNotifModel]):
            body = ""
            for mwn in mwns:
                body += mwn.original_title + "\n"
                body += mwn.original_body + "\n"
                body += "\n\n\n"
            await bot.send_message(chat_id=await feature.user.t_profile, text=body)
            for mwn in mwns:
                body += mwn.original_title + "\n"
                body += mwn.original_body + "\n"
                body += "\n\n\n"
                await MarketWatcherNotifSatisfyModel.objects.acreate(feature=feature, notif=mwns)

        task = asyncio.create_task(satisfy(feature=feature, mwns=mwns))
        tasks.append(task)
    await asyncio.gather(*tasks)
    return {"chat_count": len(tasks)}
