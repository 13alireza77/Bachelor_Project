import logging

from crawl.bot_manager import TokenManager, PostManager

if __name__ == "__main__":
    input_arg = "post"
    print(input_arg)
    logging.info(f"run {input_arg} service")
    try:
        if input_arg == "post":
            c = PostManager()
            c.manage()
        elif input_arg == "token":
            c = TokenManager()
            c.manage()
    except Exception as e:
        logging.error(f"{e}")
        print(e)
