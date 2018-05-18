import os
import hashlib
import logging
import yaml
from dictop import select
from paramiko import ServerInterface
from paramiko import SFTPServerInterface
from paramiko import SFTPServer
from paramiko import SFTPAttributes
from paramiko import SFTPHandle
from paramiko import SFTP_OK
from paramiko import AUTH_SUCCESSFUL
from paramiko import AUTH_FAILED
from paramiko import OPEN_SUCCEEDED


logger = logging.getLogger(__name__)


class StubServer (ServerInterface):
    def __init__(self, config):
        self.config = config
        self.user_db_path = os.path.expandvars(os.path.expanduser(select(self.config, "sftpd.users", "users.yml")))
        self.root = os.path.expandvars(os.path.expanduser(select(self.config, "sftpd.root", os.getcwd())))

    def make_user_root(self, username):
        self.username = username
        self.user_root = os.path.join(self.root, username)
        if not os.path.exists(self.user_root):
            os.makedirs(self.user_root, exist_ok=True)

    def check_auth_password(self, username, password):
        logger.debug("sftpd check_auth_password: username={username}".format(username=username))
        users = {}
        with open(self.user_db_path, "rb") as user_db_file:
            users = yaml.load(user_db_file)
        info = users.get(username, None)
        if not info:
            return AUTH_FAILED
        real_password = info.get("password", "")
        if not real_password:
            return AUTH_FAILED
        if real_password.lower().startswith("md5:"):
            if hashlib.md5(password.encode("utf-8")).hexdigest() == real_password[4:].lower():
                self.make_user_root(username)
                return AUTH_SUCCESSFUL
            else:
                return AUTH_FAILED
        if real_password.lower().startswith("sha1:"):
            if hashlib.sha1(password.encode("utf-8")).hexdigest() == real_password[5:].lower():
                self.make_user_root(username)
                return AUTH_SUCCESSFUL
            else:
                return AUTH_FAILED
        if real_password.lower().startswith("sha256:"):
            if hashlib.sha256(password.encode("utf-8")).hexdigest() == real_password[7:].lower():
                self.make_user_root(username)
                return AUTH_SUCCESSFUL
            else:
                return AUTH_FAILED
        if real_password == password:
            self.make_user_root(username)
            return AUTH_SUCCESSFUL
        else:
            return AUTH_FAILED
        
    def check_auth_publickey(self, username, key):
        return AUTH_FAILED
        
    def check_channel_request(self, kind, chanid):
        return OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"


class StubSFTPHandle (SFTPHandle):
    def stat(self):
        try:
            return SFTPAttributes.from_stat(os.fstat(self.readfile.fileno()))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def chattr(self, attr):
        # python doesn't have equivalents to fchown or fchmod, so we have to
        # use the stored filename
        try:
            SFTPServer.set_file_attr(self.filename, attr)
            return SFTP_OK
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)


class StubSFTPServer (SFTPServerInterface):
    def __init__(self, server, *largs, **kwargs):
        self.server = server
        self.largs = largs
        self.kwargs = kwargs

    def _realpath(self, path):
        path = os.path.realpath(self.server.user_root + self.canonicalize(path))
        return path

    def list_folder(self, path):
        path = self._realpath(path)
        try:
            out = [ ]
            flist = os.listdir(path)
            for fname in flist:
                attr = SFTPAttributes.from_stat(os.stat(os.path.join(path, fname)))
                attr.filename = fname
                out.append(attr)
            return out
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def stat(self, path):
        path = self._realpath(path)
        try:
            return SFTPAttributes.from_stat(os.stat(path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def lstat(self, path):
        path = self._realpath(path)
        try:
            return SFTPAttributes.from_stat(os.lstat(path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def open(self, path, flags, attr):
        path = self._realpath(path)
        try:
            binary_flag = getattr(os, 'O_BINARY',  0)
            flags |= binary_flag
            mode = getattr(attr, 'st_mode', None)
            if mode is not None:
                fd = os.open(path, flags, mode)
            else:
                # os.open() defaults to 0777 which is
                # an odd default mode for files
                fd = os.open(path, flags, 0o666)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        if (flags & os.O_CREAT) and (attr is not None):
            attr._flags &= ~attr.FLAG_PERMISSIONS
            SFTPServer.set_file_attr(path, attr)
        if flags & os.O_WRONLY:
            if flags & os.O_APPEND:
                fstr = 'ab'
            else:
                fstr = 'wb'
        elif flags & os.O_RDWR:
            if flags & os.O_APPEND:
                fstr = 'a+b'
            else:
                fstr = 'r+b'
        else:
            # O_RDONLY (== 0)
            fstr = 'rb'
        try:
            f = os.fdopen(fd, fstr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        fobj = StubSFTPHandle(flags)
        fobj.filename = path
        fobj.readfile = f
        fobj.writefile = f
        return fobj

    def remove(self, path):
        path = self._realpath(path)
        try:
            os.remove(path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def rename(self, oldpath, newpath):
        oldpath = self._realpath(oldpath)
        newpath = self._realpath(newpath)
        try:
            os.rename(oldpath, newpath)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def mkdir(self, path, attr):
        path = self._realpath(path)
        try:
            os.mkdir(path)
            if attr is not None:
                SFTPServer.set_file_attr(path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def rmdir(self, path):
        path = self._realpath(path)
        try:
            os.rmdir(path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def chattr(self, path, attr):
        path = self._realpath(path)
        try:
            SFTPServer.set_file_attr(path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def symlink(self, target_path, path):
        path = self._realpath(path)
        if (len(target_path) > 0) and (target_path[0] == '/'):
            # absolute symlink
            target_path = os.path.join(self.server.user_root, target_path[1:])
            if target_path[:2] == '//':
                # bug in os.path.join
                target_path = target_path[1:]
        else:
            # compute relative to path
            abspath = os.path.join(os.path.dirname(path), target_path)
            if abspath[:len(self.server.user_root)] != self.server.user_root:
                # this symlink isn't going to work anyway -- just break it immediately
                target_path = '<error>'
        try:
            os.symlink(target_path, path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def readlink(self, path):
        path = self._realpath(path)
        try:
            symlink = os.readlink(path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        # if it's absolute, remove the root
        if os.path.isabs(symlink):
            if symlink[:len(self.server.user_root)] == self.server.user_root:
                symlink = symlink[len(self.server.user_root):]
                if (len(symlink) == 0) or (symlink[0] != '/'):
                    symlink = '/' + symlink
            else:
                symlink = '<error>'
        return symlink
