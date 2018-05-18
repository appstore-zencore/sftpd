from appserver import server
from appserver import set_default_config_path
from appserver import set_default_pidfile
from appserver import set_config_loader
from appserver import default_config_loader
from dictop import update

def sftpd_loader(config):
    data = default_config_loader(config)
    update(data, "application.main", "sftpd.server.sftp_server")
    return data

def main():
    set_default_config_path("sftpd.yml")
    set_default_pidfile("sftpd.pid")
    set_config_loader(sftpd_loader)
    server()

if __name__ == "__main__":
    main()
