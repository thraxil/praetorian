# Django settings for praetorian project.
from settings_shared import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MEDIA_ROOT = '/var/www/praetorian/auctions/media/'
MEDIA_URL = ''

TEMPLATE_DIRS = (
    "/var/www/praetorian/auctions/templates/"
)

