sftpd
=====

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
    -c, --config FILENAME  Config file path, use yaml format. Default to
                            config.yaml.
    --help                 Show this message and exit.

    Commands:
    reload  Reload application server.
    start   Start application server.
    stop    Stop application server.

Example config
--------------

::

    application:
        daemon: false
        pidfile: sftpd.pid

    sftpd:
        root: /data/sftpd
        keyfile: /path/to/server-key
        users: /path/to/users.yml

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


Example users
-------------

::

    user01:
        password: user01's-password
    user02:
        password: user02's-password


Note:

1. sftpd will always reload data from users.yml while doing authentication.
