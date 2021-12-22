import logging

from crawl.bot_manager import TokenManager

logging.info(f"run token service")
try:
    c = TokenManager()
    c.manage()
except Exception as e:
    logging.error(f"{e}")
    print(e)
