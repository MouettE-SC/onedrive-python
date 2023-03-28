from onedrive import app_defaults

sync_types = ['full', 'on-demand']


class Drive:

    def __init__(self, data: dict = {}):
        self.id = ""
        self.sync = ""


class Account:

    def __init__(self, data: dict = {}):
        self.application_id: str = data.get('application_id', app_defaults.app_default_id)
        self.application_name: str = data.get('application_name', app_defaults.app_default_name)
        self.application_version: str = data.get('application_version', app_defaults.app_default_version)
        self.company_name: str = data.get('company_name', app_defaults.app_default_company_name)
        self.isv: bool = data.get('isv', app_defaults.app_default_isv)
        self.endpoint: str = data.get('endpoint', app_defaults.app_default_endpoint)
        self.tenant: str = data.get('tenant', app_defaults.app_default_tenant)
        self.drives: list[Drive] = list(map(Drive, data.get('drives', [])))

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


if __name__ == '__main__':
    import json
    a = Account()
    a.drives.append(Drive())
    o = json.dumps([a, a], default=lambda o: o.__dict__, indent=4)
    n = json.loads(o, object_hook=Account)
    print(n)
