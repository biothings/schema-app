
''' Discovery App Configuration '''


from config_key import COOKIE_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

# *****************************************************************************
# Credentials
# *****************************************************************************
# Define in <project_folder>/config_key.py:
#   COOKIE_SECRET = '<Any Random String>'
#   GITHUB_CLIENT_ID = '<your Github application Client ID>'
#   GITHUB_CLIENT_SECRET = '<your Github application Client Secret>'

# *****************************************************************************
# Elasticsearch
# *****************************************************************************
ES_INDEX = 'discover_schema_class'
ES_DOC_TYPE = 'schema'
ES_CLIENT_TIMEOUT = 10

# *****************************************************************************
# Tornado URL Patterns
# *****************************************************************************
API_PREFIX = 'api'
API_VERSION = ''
APP_LIST = [
    (r"/api/query/?", "biothings.web.api.es.handlers.QueryHandler"),
    (r"/api/registry/([^/]+)/([^/]+)/?", "discovery.web.api.RegistryHandler"),
    (r"/api/registry/([^/]+)/?", "discovery.web.api.RegistryHandler"),
    (r"/api/registry/?", "discovery.web.api.RegistryHandler"),
    (r"/api/dataset/([^/]+)/?", "discovery.web.api.MetadataHandler"),
    (r"/api/dataset/?", "discovery.web.api.MetadataHandler"),
    (r"/api/view/?", "discovery.web.api.SchemaViewHandler")
]

# *****************************************************************************
# Biothings SDK Settings
# *****************************************************************************
ACCESS_CONTROL_ALLOW_METHODS = 'HEAD,GET,POST,DELETE,PUT,OPTIONS'
ES_QUERY_BUILDER = "discovery.query.DiscoveryQueryBuilder"
DISABLE_CACHING = True