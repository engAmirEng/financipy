from datetime import timedelta

from environ import environ

from ._setup import env

# Project's apps stuff...
# ------------------------------------------------------------------------------

OPENAI_API_KEY = env.str("OPENAI_API_KEY")

# graphql
# ------------------------------------------------------------------------------
# show graphiql panel or not
GRAPHIQL = env.bool("GRAPHIQL", False)

# telegram_bot
# ------------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = env.str("TELEGRAM_WEBHOOK_URL", "telegram-webhook/")
TELEGRAM_WEBHOOK_SECRET = env.str("TELEGRAM_WEBHOOK_SECRET")
TELEGRAM_PROXY = env.url("TELEGRAM_PROXY", default=None)
if TELEGRAM_PROXY:
    TELEGRAM_PROXY = environ.urlunparse(TELEGRAM_PROXY)

TELEGRAM_MIDDLEWARE = ["financipy.telegram_bot.t_middleware.AuthenticationMiddleware"]

# fundamental_analysis
# ------------------------------------------------------------------------------
MARKET_WATCHER_NOTIF_WINDOW = timedelta(minutes=20)
