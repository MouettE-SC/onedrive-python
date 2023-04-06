import random
import string

from onedrive.account import Account
from onedrive import endpoints, def_scopes
from onedrive.config import OnedriveConfig
import typing
import logging
import urllib.parse
from requests import Session, Response, JSONDecodeError
from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtDBus import QDBusConnection
from PySide6.QtWidgets import QMessageBox
from time import time
import jwt

log = logging.getLogger('api')


class OAuth(QObject):
    def __init__(self, callback: typing.Callable[[str], None], parent: QObject):
        super().__init__(parent)
        self.callback = callback
        self.sb = QDBusConnection.sessionBus()
        if not self.sb.isConnected():
            QMessageBox.critical(parent, self.tr("DBus not available"), self.tr("Unable to connect to local session DBus. Cannot continue."))
            self.callback(None)
        elif not self.sb.registerService('org.python.onedrive'):
            QMessageBox.critical(parent, self.tr("DBus error"),
                                 self.tr("Unable to register DBus python-onedrive service"))
            log.error('Unable to register dbus service : '+self.sb.lastError().message())
            self.callback(None)
        elif not self.sb.registerObject('/', self, QDBusConnection.RegisterOption.ExportAllSlots):
            QMessageBox.critical(parent, self.tr("DBus error"),
                                 self.tr("Unable to register DBus python-onedrive object"))
            log.error('Unable to register dbus oauth object : ' + self.sb.lastError().message())
            self.callback(None)

    def cancel(self):
        self.sb.unregisterObject('/')
        if not self.sb.unregisterService('org.python.onedrive'):
            log.error('Unable to unregister dbus service : ' + self.sb.lastError().message())

    @Slot(str, result=None)
    def oauth(self, url):
        log.debug("Received DBus url callback with url="+url)
        self.cancel()
        self.callback(url)


class OneDriveAPI(QObject):

    def __init__(self, config: OnedriveConfig, account: Account, parent: QObject):
        super().__init__(parent)
        self.config = config
        self.account = account
        self.endpoint = endpoints[self.account.endpoint]
        self.auth_url = self.endpoint['auth'] + "/" + self.account.tenant + "/oauth2/v2.0/authorize"
        self.token_url = self.endpoint['auth'] + "/" + self.account.tenant + "/oauth2/v2.0/token"
        self.drive_url = self.endpoint['graph'] + "/v1.0/me/drive"
        self.drive_by_id_url = self.endpoint['graph'] + "/v1.0/drives/"
        self.shared_with_me_url = self.endpoint['graph'] + "/v1.0/me/drive/sharedWithMe"
        self.item_by_id_url = self.endpoint['graph'] + "/v1.0/me/drive/items/"
        self.item_by_path_url = self.endpoint['graph'] + "/v1.0/me/drive/root:/"
        self.site_search_url = self.endpoint['graph'] + "/v1.0/sites?search"
        self.site_drive_url = self.endpoint['graph'] + "/v1.0/sites/"
        self.subscription_url = self.endpoint['graph'] + "/v1.0/subscriptions"
        self.auth_cb: typing.Callable[[bool], None] = None
        self.r_session = Session()
        self.r_session.headers.update({'User-Agent': self.account.get_user_agent()})
        self.oauth: OAuth = None
        self.state = ''

    def start_auth(self, callback: typing.Callable[[bool], None]):
        log.info('Starting oauth login process')
        self.auth_cb = callback
        self.oauth = OAuth(self.oauth_cb, self.parent())
        self.state = ''.join(random.choice(string.ascii_letters+string.digits) for i in range(32))
        url = QUrl(self.auth_url+'?client_id='+self.account.application_id+"&response_type=code&redirect_uri=onedrive://oauth&response_mode=query&scope="+" ".join(def_scopes)+"&state="+self.state)
        log.debug("Opening URL "+url.toString())
        QDesktopServices.openUrl(url)

    def oauth_cb(self, url):
        self.oauth = None
        if url is None:
            self.auth_cb(False)
        query_data = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        try:
            if 'error' in query_data:
                if query_data['error'][0] == 'access_denied':
                    QMessageBox.critical(self.parent(), self.tr('Error'), self.tr('Access denied'))
                else:
                    QMessageBox.critical(self.parent(), self.tr('Error'), query_data['error'][0])
                self.auth_cb(False)
                return
            elif query_data['state'][0] != self.state:
                QMessageBox.critical(self.parent(), self.tr('Error'), self.tr('Invalid request received from browser (non-consistent state)'))
                self.auth_cb(False)
                return
            log.info("Received authorization code, requesting initial tokens")
            payload = {
                'client_id': self.account.application_id,
                'grant_type': 'authorization_code',
                'scope' : ' '.join(def_scopes),
                'code': query_data['code'][0],
                'redirect_uri': 'onedrive://oauth'
            }
            now = time()
            r: Response = self.r_session.post(self.token_url, data=payload)
            try:
                r_data = r.json()
            except JSONDecodeError:
                log.exception(f"Invalid JSON returned for access token exchange (status_code={r.status_code})")
                QMessageBox.critical(self.parent(), self.tr("Error"),
                                     self.tr('Error while negociating authentication tokens'))
                self.auth_cb(False)
                return
            if 200 <= r.status_code < 300:
                r_scopes = r_data['scope'].split()
                if 'refresh_token' not in r_data:
                    log.info("User did not grant offline_access authorization")
                    QMessageBox.critical(self.parent(), self.tr("Error"),
                                         self.tr('You must allow offline_access for this application to work'))
                    self.auth_cb(False)
                    return
                elif 'id_token' not in r_data:
                    log.info("id_token not present in token data")
                    QMessageBox.critical(self.parent(), self.tr("Error"),
                                         self.tr('Error while negociating authentication tokens'))
                    self.auth_cb(False)
                id_token = jwt.decode(r_data['id_token'], options={'verify_signature': False})
                self.account.oid = id_token['oid']
                self.account.tid = id_token['tid']
                self.account.description = f"{id_token['name']} <{id_token['preferred_username']}>"
                self.account.scopes = r_scopes
                self.account.access_token = r_data['access_token']
                self.account.refresh_token = r_data['refresh_token']
                self.account.expiration = now + r_data['expires_in']
                log.info("Successfully obtained access and refresh tokens, saving new account information")
                self.config.add_account(self.account)
                self.auth_cb(True)
            else:
                if 'error' in r_data:
                    print(r_data)
                    log.error(f"Invalid response {r.status_code} for initial token request: {r_data['error']['code']}/{r_data['error']['message']}")
                else:
                    log.error(f"Invalid response {r.status_code} for initial token request")
                QMessageBox.critical(self.parent(), self.tr("Error"),
                                     self.tr('Error while negociating authentication tokens'))
                self.auth_cb(False)
        except:
            log.exception('Error while finalizing OAuth token negociation')
            QMessageBox.critical(self.parent(), self.tr("Error"),
                                 self.tr('Error while negociating authentication'))
            self.auth_cb(False)


    def cancel_auth(self):
        if self.oauth:
            log.debug("Cancelling oauth login")
            self.oauth.cancel()
