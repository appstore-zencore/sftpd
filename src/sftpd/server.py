import os
import time
import socket
import signal
import threading
import logging
import yaml
import paramiko
from dictop import select
import click
from .simple import StubServer
from .simple import StubSFTPServer
from .utils import setup_logging
from .utils import setup_signal_hook


stop_flag = threading.Event()
logger = logging.getLogger(__name__)


def sftp_server(config):
    logging.debug("sftp server starting with config = {config}.".format(config=config))
    setup_logging(config)
    setup_signal_hook(stop_flag)

    binding = select(config, "server.binding", "0.0.0.0")
    port = select(config, "server.port", 2022)
    backlog = select(config, "server.backlog", 1024)
    accept_timeout = select(config, "server.accept-timeout", 2)
    keyfile = os.path.expandvars(os.path.expanduser(select(config, "sftpd.keyfile", "~/.ssh/id_rsa")))

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

    logging.info("sftp server wating connection...")
    while not stop_flag.is_set():
        try:
            remote_connection, remote_address = server_socket.accept()
        except socket.timeout:
            logger.debug("sftp server got no connection, try again...")
            continue
        logger.info("sftp server got a connection: {remote_address}.".format(remote_address=remote_address))
        host_key = paramiko.RSAKey.from_private_key_file(keyfile)
        transport = paramiko.Transport(remote_connection)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler('sftp', paramiko.SFTPServer, StubSFTPServer)
        transport.start_server(event=threading.Event(), server=StubServer(config))
        logger.info("a new transport was started: {transport}.".format(transport=transport))

    logger.info("sftp server stopped.")
