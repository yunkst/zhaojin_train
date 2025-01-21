from plugins.logger import setup_logger

logger = setup_logger()


def test_log_info():
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
