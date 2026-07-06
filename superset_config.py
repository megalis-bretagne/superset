###################################################################################
# Using custom security manager
#
from flask import Flask
from flask_appbuilder.security.manager import AUTH_OID

from custom.keycloak_security_manager import OIDCSecurityManager, oidc_check_loggedin_or_logout
from cachelib.file import FileSystemCache
AUTH_TYPE = AUTH_OID
CUSTOM_SECURITY_MANAGER = OIDCSecurityManager
CUSTOM_AUTH_USER_REGISTRATION_ROLE = "Public" # Role de base par défaut synchronisé lors du login

# Longévité de la session superset
# PERMANENT_SESSION_LIFETIME = 30

############### KEYCLOACK ##########
OIDC_CLIENT_SECRETS =  "/app/pythonpath/custom/client_secret.json"
OIDC_ID_TOKEN_COOKIE_SECURE = False
OIDC_OPENID_REALM= "megalis"
OIDC_INTROSPECTION_AUTH_METHOD= "client_secret_post"
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Public'
PUBLIC_ROLE_LIKE = "Gamma"
AUTH_ROLE_PUBLIC = 'Public'


#####################################
APP_NAME = "Superset Megalis"

ROW_LIMIT = 10000000
# ajout CRI le 20251001
# Augmenter la limite de lignes exportables en CSV
CSV_MAX_ROWS = 100000

# Augmenter la limite pour l'exportation vers Excel
EXCEL_MAX_ROWS = 100000
# fin ajout CRI
CSV_EXPORT_MAX_ROWS =10000000 
FILTER_SELECT_ROW_LIMIT = 10000

# Flask App Builder configuration
# Your App secret key will be used for securely signing the session cookie
# and encrypting sensitive information on the database
# Make sure you are changing this key for your deployment with a strong key.
# Alternatively you can set it with `SUPERSET_SECRET_KEY` environment variable.
# You MUST set this for production environments or the server will not refuse
# to start and you will see an error in the logs accordingly.
SECRET_KEY = "MEGALIS_KEY_COMPLEXE_SUPERSET"

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
SQLALCHEMY_DATABASE_URI =  "postgresql://superset:QrBQeanbjEg992n@hbmegtools01p:5433/superset"

DATABASE_DIALECT ="postgresql"
DATABASE_USER = "superset"
DATABASE_PASSWORD = "QrBQeanbjEg992n"
DATABASE_HOST = "hbmegtools01p"
DATABASE_PORT = 5433
DATABASE_DB = "superset"

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_CELERY_DB = 0
REDIS_RESULTS_DB = 1

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")


CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG


# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = [
    "superset.views.core.log",
    "superset.views.core.explore_json",
    "superset.charts.data.api.data",
 
    'custom.keycloak_security_manager.sso_logout',
    'custom.keycloak_security_manager.login',
    'custom.keycloak_security_manager.logout',
]# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''

ENABLE_PROXY_FIX = True
LANGUAGES = {
    'fr': {'flag': 'fr', 'name': 'French'},
    "en": {"flag": "us", "name": "English"},
}

FEATURE_FLAGS = {'TAGGING_SYSTEM': True}

# Partie Alert & Report, non utilisé sur Megalis pour le moment

# class CeleryConfig(object):
#     BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
#     CELERY_IMPORTS = ("superset.sql_lab",)
#     CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
#     CELERYD_LOG_LEVEL = "DEBUG"
#     CELERYD_PREFETCH_MULTIPLIER = 1
#     CELERY_ACKS_LATE = False
#     CELERYBEAT_SCHEDULE = {
#         "reports.scheduler": {
#             "task": "reports.scheduler",
#             "schedule": crontab(minute="*", hour="*"),
#         },
#         "reports.prune_log": {
#             "task": "reports.prune_log",
#             "schedule": crontab(minute=10, hour=0),
#         },
#     }


# CELERY_CONFIG = CeleryConfig

# FEATURE_FLAGS = {"ALERT_REPORTS": True}
# ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
# WEBDRIVER_BASEURL = "http://superset:8088/"
# # The base URL for the email report hyperlinks.
# WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL


# ADDITIONAL_MIDDLEWARE = [AuthMiddleware, ]

TALISMAN_CONFIG = {
    "force_https": True,
    "content_security_policy": {
        "default-src": ["'self'", "*.megalis.bretagne.bzh", "*.geobretagne.fr"],
        "img-src": ["*", "data:", "'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "frame-src": [
            "'self'",
            "*.megalis.bretagne.bzh",
            "geobretagne.fr",
        ],
        "frame-ancestors": [
            "'self'",
            "*.megalis.bretagne.bzh",
            "geobretagne.fr",
        ],
        "script-src": ["'self'", "'unsafe-eval'", "'unsafe-inline'", "blob:"],
    },
}

HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    "attributes": {"*": ["style", "className"], "iframe": ["src"]},
    "tagNames": ["style", "iframe"],
}


def FLASK_APP_MUTATOR(app: Flask):
    @app.before_request
    def before_request():
        oidc_check_loggedin_or_logout()


####################################################################################
