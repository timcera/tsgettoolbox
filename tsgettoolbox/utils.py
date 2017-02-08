
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp

from tsgettoolbox import appdirs

dirs = appdirs.AppDirs('tsgettoolbox', 'tsgettoolbox')


def read_api_key(service):
    # Read in API key
    if not os.path.exists(dirs.user_config_dir):
        os.makedirs(dirs.user_config_dir)
    configfile = os.path.join(dirs.user_config_dir, 'config.ini')
    if not os.path.exists(configfile):
        with open(configfile, 'w') as fp:
            fp.write('''

[{0}]
api_key = ReplaceThisStringWithYourKey

'''.format(service))
    # Make sure read only by user.
    os.chmod(configfile, 0o600)

    inifile = cp.ConfigParser()
    inifile.readfp(open(configfile, 'r'))

    try:
        api_key = inifile.get(service, 'api_key')
    except:
        with open(configfile, 'a') as fp:
            fp.write('''

[{0}]
api_key = ReplaceThisStringWithYourKey

'''.format(service))
        api_key = 'ReplaceThisStringWithYourKey'

    inifile.readfp(open(configfile, 'r'))
    api_key = inifile.get(service, 'api_key')
    if api_key == 'ReplaceThisStringWithYourKey':
        raise ValueError('''
*
*   Need to edit {0}
*   to add your API key that you got from {1}.
*
'''.format(configfile, service))

    return api_key
