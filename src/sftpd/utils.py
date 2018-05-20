import os
import click
import signal
import logging
from logging import config as logging_config
from dictop import select


logger = logging.getLogger(__name__)


def setup_logging(config):
    logging_config_data = select(config, "logging")
    if not logging_config_data:
        logging.basicConfig()
    elif logging_config_data and isinstance(logging_config_data, dict) and hasattr(logging_config, "dictConfig"):
        logging_config.dictConfig(logging_config_data)
    elif logging_config_data and isinstance(logging_config_data, str):
        logging_config.fileConfig(logging_config_data)


def setup_signal_hook(stop_flag):
    stop_flag.clear()
    def on_exit(sig, frame):
        stop_flag.set()
        msg = "Server got signal {sig}, set stop_flag=True and exiting...".format(sig=sig)
        click.echo(msg, file=os.sys.stderr)
        logger.info(msg)
    try:
        signal.signal(signal.SIGINT, on_exit)
        signal.signal(signal.SIGTERM, on_exit)
    except:
        logger.exception("Install signal failed, but program will keep on running...")
