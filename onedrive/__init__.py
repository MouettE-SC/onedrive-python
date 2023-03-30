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
    'app_default_id': "b738e7eb-4132-43e2-8fb9-27198b8a1263",
    'app_default_name': "OneDriveFUSE",
    'app_default_company_name': "la-mouette",
    'app_default_isv': True,
    'app_default_endpoint': "Global",
    'app_default_tenant': "common",
    'app_default_version': VERSION
}
