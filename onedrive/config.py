from configparser import ConfigParser
import json
from onedrive.account import Account
import logging
import logging.handlers
import sys
import os

log = logging.getLogger('config')


class OnedriveConfig:

    def __init__(self, ini: str):
        self.ini = ini
        self.conf = ConfigParser()
        def_conf = os.path.join(os.path.dirname(__file__), "default.ini")
        self.conf.read_file(open(def_conf))
        if "XDG_CACHE_HOME" in os.environ:
            self.conf.set('directories', 'cache', os.path.join(os.getenv("XDG_CACHE_HOME"), 'onedrive'))
        if "XDG_DATA_HOME" in os.environ:
            self.conf.set('directories', 'data', os.path.join(os.getenv("XDG_DATA_HOME"), 'onedrive'))
        if os.path.exists(ini):
            self.conf.read(ini, encoding="utf8")
        self.setup_logging()

        self.setup_dirs()
        self.accounts_conf = os.path.join(self.get_dir('data'), 'accounts.json')
        self.accounts: list[Account] = []
        self.load_accounts()

        if not os.path.exists(ini):
            self.save_conf()

    def setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.conf.get('logging', 'level').upper())
        if self.conf.getboolean('logging', 'timestamp'):
            log_format = logging.Formatter("%(asctime)s - %(name)s - [%(levelname)s] %(message)s")
        else:
            log_format = logging.Formatter("%(name)s - [%(levelname)s] %(message)s")
        if self.conf.get('logging', 'output') == 'console':
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(log_format)
            root_logger.addHandler(ch)
        else:
            fh = logging.handlers.RotatingFileHandler(self.conf.get('logging', 'output'), maxBytes=5242880, backupCount=14)
            fh.setFormatter(log_format)
            root_logger.addHandler(fh)
        logging.captureWarnings(True)

    def save_conf(self):
        os.makedirs(os.path.dirname(self.ini))
        with open(self.ini, 'w') as f:
            self.conf.write(f)

    def get_dir(self, d):
        return os.path.expandvars(self.conf.get('directories', d))

    def setup_dirs(self):
        os.makedirs(self.get_dir('cache'), exist_ok=True)
        os.makedirs(self.get_dir('data'), exist_ok=True)

    def save_accounts(self):
        log.debug("Saving account configuration")
        with open(self.accounts_conf, 'w') as f:
            json.dump(self.accounts, f, default=lambda o: o.__dict__, indent=4)

    def load_accounts(self):
        if not os.path.exists(self.accounts_conf):
            self.save_accounts()
        else:
            with open(self.accounts_conf, 'r') as f:
                self.accounts = json.load(f, object_hook=Account)
            log.debug("Loaded %i accounts configurations" % (len(self.accounts), ))