"""gae_pathfix.py
Quick fix to use py.test with Flask on GAE.

Working 2015-01-16 with:
    * GAE 1.9.17
    * Python 2.7.6
    * Flask 0.10.1
    * py.test 2.6.4

Usage:
1. Copy gae_pathfix.py to your py.test module
2. `import gae_pathfix` in the __init__.py file of your py.test module
3. Ensure that `PATH_TO_DEV_APPSERVER` is correct for your installation
    * the default below should work for homebrew installs,
      `brew install google-app-engine`

"""

import sys
import os

# Path to the *directory* containing dev_appserver.py
PATH_TO_DEV_APPSERVER = "/usr/local/bin"

# If envvar GAE_DIR is set (as in travis-ci), use that value. Otherwise,
# use the value set above.
sys.path.append(os.getenv('GAE_DIR', PATH_TO_DEV_APPSERVER))

import dev_appserver
sys.path.extend(dev_appserver.EXTRA_PATHS)

from google.appengine.ext import testbed

testbed = testbed.Testbed()
testbed.activate()

# If you have PIL installed, you can just use:
# testbed.init_all_stubs()

# If you don't have PIL installed, you have to manually deselect the
# images_stub and init the rest. You may be able to speed
# things up by only selecting the ones you need and commenting the rest.

# testbed.init_images_stub()
testbed.init_app_identity_stub()
testbed.init_blobstore_stub()
testbed.init_capability_stub()
testbed.init_channel_stub()
testbed.init_datastore_v3_stub()
testbed.init_files_stub()
testbed.init_logservice_stub()
testbed.init_mail_stub()
testbed.init_memcache_stub()
testbed.init_taskqueue_stub()
testbed.init_urlfetch_stub()
testbed.init_user_stub()
testbed.init_xmpp_stub()
