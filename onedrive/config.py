from configparser import ConfigParser
import json
from onedrive.account import Account
from onedrive import VERSION
import logging
import logging.handlers
import sys
import os
from string import Template

log = logging.getLogger('config')
_UNSET=object()

class OnedriveConfig(ConfigParser):

    def __init__(self, ini: str):
        super().__init__()
        self.ini = ini
        def_conf = os.path.join(os.path.dirname(__file__), "default.ini")
        self.read_file(open(def_conf))
        if "XDG_CACHE_HOME" in os.environ:
            self.set('directories', 'cache', os.path.join(os.getenv("XDG_CACHE_HOME"), 'onedrive'))
        if "XDG_DATA_HOME" in os.environ:
            self.set('directories', 'data', os.path.join(os.getenv("XDG_DATA_HOME"), 'onedrive'))
        if os.path.exists(ini):
            self.read(ini, encoding="utf8")
        else:
            with open(def_conf, 'r') as i, open(ini, 'w') as o:
                src = Template(i.read())
                o.write(src.substitute({'version': VERSION}))

        self.setup_logging()

        self.setup_dirs()
        self.accounts_conf = os.path.join(self.get_dir('data'), 'accounts.json')
        self.accounts: dict[str, Account] = {}
        self.load_accounts()

        if not os.path.exists(ini):
            self.save_conf()

    def setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.get('logging', 'level').upper())
        if self.getboolean('logging', 'timestamp'):
            log_format = logging.Formatter("%(asctime)s - %(name)s - [%(levelname)s] %(message)s")
        else:
            log_format = logging.Formatter("%(name)s - [%(levelname)s] %(message)s")
        if self.get('logging', 'output') == 'console':
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(log_format)
            root_logger.addHandler(ch)
        else:
            fh = logging.handlers.RotatingFileHandler(self.get('logging', 'output'), maxBytes=5242880, backupCount=14)
            fh.setFormatter(log_format)
            root_logger.addHandler(fh)
        logging.captureWarnings(True)

    def save_conf(self):
        os.makedirs(os.path.dirname(self.ini))
        with open(self.ini, 'w') as f:
            self.write(f)

    def get_dir(self, d):
        return os.path.expandvars(self.get('directories', d))

    def setup_dirs(self):
        os.makedirs(self.get_dir('cache'), exist_ok=True)
        os.makedirs(self.get_dir('data'), exist_ok=True)

    def save_accounts(self):
        log.info("Saving account configuration")
        with open(self.accounts_conf, 'w') as f:
            json.dump(list(self.accounts.values()), f, default=lambda o: o.__dict__, indent=4)

    def load_accounts(self):
        if not os.path.exists(self.accounts_conf):
            self.save_accounts()
        else:
            with open(self.accounts_conf, 'r') as f:
                for a in json.load(f, object_hook=Account):
                    self.accounts[a.oid] = a
            log.debug("Loaded %i accounts configurations" % (len(self.accounts), ))

    def add_account(self, account: Account):
        self.accounts[account.oid] = account
        self.save_accounts()

    def remove_account(self, account: Account):
        if self.accounts.pop(account.oid, None):
            self.save_accounts()
