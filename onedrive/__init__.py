VERSION = "0.1"

# See https://learn.microsoft.com/en-us/graph/deployments
endpoints = {
    'Global': {
        'name': 'Global',
        'auth': 'https://login.microsoftonline.com',
        'graph': 'https://graph.microsoft.com'
    },
    'USL4': {
        'name': 'US Government L4',
        'auth': 'https://login.microsoftonline.us',
        'graph': 'https://graph.microsoft.us'
    },
    'USL5': {
        'name': 'US Government L5',
        'auth': 'https://login.microsoftonline.us',
        'graph': 'https://dod-graph.microsoft.us'
    },
    'DE': {
        'name': 'Germany',
        'auth': 'https://login.microsoftonline.de',
        'graph': 'https://graph.microsoft.de'
    },
    'CN': {
        'name': 'China (21Vianet)',
        'auth': 'https://login.chinacloudapi.cn',
        'graph': 'https://microsoftgraph.chinacloudapi.cn'
    }
}

app_defaults = {
    'endpoint': "Global",
    'id': "413e73c0-43ab-4b3b-85dc-03c5a6684787",
    'name': "Onedrive Fuse for Linux",
    'company_name': "M LECLERC CHARLES",
    'isv': True,
    'tenant': "common",
    'version': VERSION
}

def_scopes = ['Files.ReadWrite',
              'Files.ReadWrite.All',
              'offline_access',
              'openid',
              'profile',
              'Sites.ReadWrite.All']