from onedrive.account import Account


class OneDriveAPI:

    def __init__(self, account: Account):
        self.account = account
        self.endpoint = endpoints[self.account.endpoint]
        self.auth_url = self.endpoint['auth'] + "/" + self.account.tenant + "/" + "/oauth2/v2.0/authorize"
        self.token_url = self.endpoint['auth'] + "/" + self.account.tenant + "/" + "/oauth2/v2.0/token"
        self.drive_url = self.endpoint['graph'] + "/v1.0/me/drive"
        self.drive_by_id_url = self.endpoint['graph'] + "/v1.0/drives/"
        self.shared_with_me_url = self.endpoint['graph'] + "/v1.0/me/drive/sharedWithMe"
        self.item_by_id_url = self.endpoint['graph'] + "/v1.0/me/drive/items/"
        self.item_by_path_url = self.endpoint['graph'] + "/v1.0/me/drive/root:/"
        self.site_search_url = self.endpoint['graph'] + "/v1.0/sites?search"
        self.site_drive_url = self.endpoint['graph'] + "/v1.0/sites/"
        self.subscription_url = self.endpoint['graph'] + "/v1.0/subscriptions"

