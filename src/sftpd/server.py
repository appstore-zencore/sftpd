import os
import time
import socket
import signal
import threading
import logging
from logging import config as logging_config
import yaml
import paramiko
from .simple import StubServer
from .simple import StubSFTPServer
from dictop import select
import click


stop_flag = threading.Event()
logger = logging.getLogger(__name__)


def sftp_service(config, connection, address):
    keyfile = os.path.expandvars(os.path.expanduser(select(config, "sftpd.keyfile", "~/.ssh/id_rsa")))
    host_key = paramiko.RSAKey.from_private_key_file(keyfile)
    transport = paramiko.Transport(connection)
    transport.add_server_key(host_key)
    transport.set_subsystem_handler('sftp', paramiko.SFTPServer, StubSFTPServer)
    server = StubServer(config)
    transport.start_server(server=server)

    channel = transport.accept()
    while transport.is_active():
        time.sleep(1)

def sftp_server(config):
    # setup logging
    logging_config_data = select(config, "logging")
    if not logging_config_data:
        logging.basicConfig()
    elif logging_config_data and isinstance(logging_config_data, dict) and hasattr(logging_config, "dictConfig"):
        logging_config.dictConfig(logging_config_data)
    elif logging_config_data and isinstance(logging_config_data, str):
        logging_config.fileConfig(logging_config_data)
    # catch signal and stop server
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
    # server
    logging.debug("sftp server starting with config = {config}.".format(config=config))
    binding = select(config, "server.binding", "0.0.0.0")
    port = select(config, "server.port", 2022)
    backlog = select(config, "server.backlog", 1024)
    accept_timeout = select(config, "server.accept-timeout", 2)
    logging.debug("sftp server start socket listening: binding={binding}, port={port}, backlog={backlog}.".format(
        binding=binding,
        port=port,
        backlog=backlog,
    ))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server_socket.setblocking(False)
    server_socket.settimeout(accept_timeout)
    server_socket.bind((binding, port))
    server_socket.listen(backlog)

    logging.debug("sftp server wating connection...")
    while not stop_flag.is_set():
        try:
            remote_connection, remote_address = server_socket.accept()
        except socket.timeout:
            continue
        logging.info("sftp server got a connection: {remote_address}.".format(remote_address=remote_address))
        service_thread = threading.Thread(target=sftp_service, args=(config, remote_connection, remote_address))
        service_thread.setDaemon(True)
        service_thread.start()

    logger.info("sftp server stopped.")
