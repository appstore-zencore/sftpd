sftpd
=====

.. image:: https://travis-ci.org/appstore-zencore/sftpd.svg?branch=master
    :target: https://travis-ci.org/appstore-zencore/sftpd

A simple multi-thread sftp server.

Install
-------

::

    pip install sftpd


Usage
-----

::

    E:\code\appstart>sftpd --help
    Usage: sftpd [OPTIONS] COMMAND [ARGS]...

    Options:
    -c, --config FILENAME  Config file path, use yaml format.
    --help                 Show this message and exit.

    Commands:
    reload  Reload application server.
    start   Start application server.
    stop    Stop application server.

Example start
-------------

::

    D:\sftpd>dir

    D:\sftpd 

    2018/05/18  20:51    <DIR>          .
    2018/05/18  20:51    <DIR>          ..
    2018/05/18  20:39             1,036 sftpd.yml
    2018/05/18  20:06                36 users.yml
                2 files          1,072 bytes
                2 folders 289,594,834,944 bytes

    C:\Users\zencore\Documents\GitHub\sftpd\src>python -m sftpd.application start
    2018-05-18 20:39:30,548 DEBUG   sftp server starting with config = {'application': {'daemon': False, 'main': 'sftpd.server.sftp_server'}, 'server': {'binding': '0.0.0.0', 'port': 2222, 'backlog': 32}, 'sftpd': {'root': 'e:/sftpd', 'keyfile': '~/.ssh/id_rsa', 'users': 'users.yml'}, 'logging': {'version': 1, 'disable_existing_loggers': False, 'formatters': {'simple': {'format': '%(asctime)-15s\t%(levelname)s\t%(message)s'}}, 'handlers': {'console': {'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'simple'}, 'file': {'class': 'logging.handlers.TimedRotatingFileHandler', 'level': 'DEBUG', 'formatter': 'simple', 'filename': 'server.log', 'backupCount': 30, 'when': 'D', 'interval': 1, 'encoding': 'utf-8'}}, 'loggers': {'sftpd': {'level': 'DEBUG', 'handlers': ['file', 'console'], 'propagate': False}}, 'root': {'level': 'DEBUG', 'handlers': ['file', 'console']}}}.
    2018-05-18 20:39:30,548 DEBUG   sftp server start socket listening: binding=0.0.0.0, port=2222, backlog=32.
    2018-05-18 20:39:30,564 DEBUG   sftp server wating connection...

    D:\sftpd>sftpd start
    2018-05-18 20:52:01,012 DEBUG   sftp server starting with config = {'application': {'daemon': False, 'main': 'sftpd.server.sftp_server'}, 'server': {'binding': '0.0.0.0', 'port': 2222, 'backlog': 32}, 'sftpd': {'root': 'e:/sftpd', 'keyfile': '~/.ssh/id_rsa', 'users': 'users.yml'}, 'logging': {'version': 1, 'disable_existing_loggers': False, 'formatters': {'simple': {'format': '%(asctime)-15s\t%(levelname)s\t%(message)s'}}, 'handlers': {'console': {'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'simple'}, 'file': {'class': 'logging.handlers.TimedRotatingFileHandler', 'level': 'DEBUG', 'formatter': 'simple', 'filename': 'server.log', 'backupCount': 30, 'when': 'D', 'interval': 1, 'encoding': 'utf-8'}}, 'loggers': {'sftpd': {'level': 'DEBUG', 'handlers': ['file', 'console'], 'propagate': False}}, 'root': {'level': 'DEBUG', 'handlers': ['file', 'console']}}}.
    2018-05-18 20:52:01,027 DEBUG   sftp server start socket listening: binding=0.0.0.0, port=2222, backlog=32.
    2018-05-18 20:52:01,043 DEBUG   sftp server wating connection...


Example config
--------------

::

    application:
        daemon: true
        pidfile: sftpd.pid

    server:
        binding: 0.0.0.0
        port: 2222
        backlog: 32

    sftpd:
        root: e:/sftpd
        keyfile: ~/.ssh/id_rsa
        users: users.yml

    logging:
        version: 1
        disable_existing_loggers: false
        formatters:
            simple:
                format: "%(asctime)-15s\t%(levelname)s\t%(message)s"
        handlers:
            console:
                class: logging.StreamHandler
                level: DEBUG
                formatter: simple
            file:
                class: logging.handlers.TimedRotatingFileHandler
                level: DEBUG
                formatter: simple
                filename: server.log
                backupCount: 30
                when: D
                interval: 1
                encoding: utf-8
        loggers:
            sftpd:
                level: DEBUG
                handlers:
                    - file
                    - console
                propagate: no
        root:
            level: DEBUG
            handlers:
                - file
                - console

Note:

1. sftpd.root defaults to os.getcwd().
2. sftpd.keyfile defaults to ~/.ssh/id_rsa.
3. You can use ssh-keygen to generate server key.
4. sftpd.users defaults to users.yml, it is yaml format config file contains users and users' password.


Example users
-------------

::

    user01:
        password: user01's-password
    user02:
        password: user02's-password


Note:

1. sftpd will always reload data from users.yml while doing authentication.
