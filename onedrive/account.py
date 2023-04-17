from onedrive import app_defaults, consumer_tid

sync_types = ['full', 'on-demand']


class Drive:

    def __init__(self, data: dict = {}):
        self.id = data.get('id', '')
        self.sync = data.get('sync', '')


class Account:

    def __init__(self, data: dict = {}):
        self.application_id: str = data.get('application_id', app_defaults['id'])
        self.application_name: str = data.get('application_name', app_defaults['name'])
        self.application_version: str = data.get('application_version', app_defaults['version'])
        self.company_name: str = data.get('company_name', app_defaults['company_name'])
        self.isv: bool = data.get('isv', app_defaults['isv'])
        self.endpoint: str = data.get('endpoint', app_defaults['endpoint'])
        self.tenant: str = data.get('tenant', app_defaults['tenant'])
        self.drives: list[Drive] = list(map(Drive, data.get('drives', [])))
        self.oid = data.get('oid', '')
        self.tid = data.get('tid', '')
        self.description = data.get('description', '')
        self.access_token = data.get('access_token', '')
        self.scopes = data.get('scopes', [])
        self.expiration = data.get('expiration', 0.)
        self.refresh_token = data.get('refresh_token', '')


    # see https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online
    def get_user_agent(self):
        if self.isv:
            res = "ISV|"
        else:
            res = "NONISV|"
        res += self.company_name + "|"
        res += self.application_name + "/"
        res += self.application_version
        return res

    def is_business(self):
        return self.tid == consumer_tid

    def reset_auth(self):
        self.access_token = ''
        self.scopes = []
        self.expiration = 0.
        self.refresh_token = ''