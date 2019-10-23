# this is the local grouprise configuration
# you may override any options that grouprise provides in its default settings.py file.
# this file is imported once the default settings.py was loaded
from stadt.settings.default import *  # noqa: F401, F403

#################################################
#
#      PLEASE SET THE FOLLOWING OPTIONS
#
#################################################
#
# SECRET_KEY = 'YOUR_SECRET_KEY'
# ALLOWED_HOSTS = ['example.com', 'localhost']
#
# ADMINS = [
#     ('Admins', 'administration@example.com'),
# ]
#
# OPERATOR_GROUP_ID = 1
#
#################################################

# set debug mode to false
DEBUG = False

# increase session cookie time to 1 year
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365
