from environ import environ

from ._setup import env

# Project stuff...
# ------------------------------------------------------------------------------
# show graphiql panel or not
GRAPHIQL = env.bool("GRAPHIQL", False)

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")

PROXY = env.url("PROXY", default=None)
if PROXY:
    PROXY = environ.urlunparse(PROXY)
