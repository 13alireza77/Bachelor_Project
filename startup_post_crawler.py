import logging

from crawl.bot_manager import PostManager

logging.info(f"run post service")
try:
    c = PostManager()
    c.manage()
except Exception as e:
    logging.error(f"{e}")
    print(e)
