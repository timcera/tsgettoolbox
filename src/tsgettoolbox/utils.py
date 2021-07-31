# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp

from tsgettoolbox import appdirs

dirs = appdirs.AppDirs("tsgettoolbox", "tsgettoolbox")


def read_api_key(service):
    # Read in API key
    if not os.path.exists(dirs.user_config_dir):
        os.makedirs(dirs.user_config_dir)
    configfile = os.path.join(dirs.user_config_dir, "config.ini")
    if not os.path.exists(configfile):
        with open(configfile, "w") as fp:
            fp.write(
                """

[{}]
api_key = ReplaceThisStringWithYourKey

""".format(
                    service
                )
            )
    # Make sure read only by user.
    os.chmod(configfile, 0o600)

    inifile = cp.ConfigParser()
    inifile.readfp(open(configfile, "r"))

    try:
        api_key = inifile.get(service, "api_key")
    except BaseException:
        with open(configfile, "a") as fp:
            fp.write(
                """

[{}]
api_key = ReplaceThisStringWithYourKey

""".format(
                    service
                )
            )
        api_key = "ReplaceThisStringWithYourKey"

    inifile.readfp(open(configfile, "r"))
    api_key = inifile.get(service, "api_key")
    if api_key == "ReplaceThisStringWithYourKey":
        raise ValueError(
            """
*
*   Need to edit {}
*   to add your API key that you got from {}.
*
""".format(
                configfile, service
            )
        )

    return api_key


def requests_retry_session(
    retries=3,
    backoff_factor=0.5,
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
