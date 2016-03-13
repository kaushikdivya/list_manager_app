"""
"""

import os
env = os.environ.get('LIST_MANAGER_ENV', 'dev')

from base import *

if env == 'dev':
    from dev import *
elif env == 'staging':
    from staging import *
elif env == 'prod':
    from prod import *

