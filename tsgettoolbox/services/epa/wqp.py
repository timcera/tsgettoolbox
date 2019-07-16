from __future__ import absolute_import
from __future__ import print_function

import logging
import os
from builtins import object
from io import BytesIO

from tsgettoolbox.odo import convert
from tsgettoolbox.odo import odo
from tsgettoolbox.odo import resource

import pandas as pd

import requests

from tstoolbox import tsutils

# EPA


class EPA_CSV(object):
    def __init__(self, url, **query_params):
        # Need to enforce waterml format
        query_params["mimeType"] = "csv"
        try:
            query_params["startDateLo"] = tsutils.parsedate(
                query_params["startDateLo"], strftime="%m-%d-%Y"
            )
        except KeyError:
            pass
        try:
            query_params["startDateHi"] = tsutils.parsedate(
                query_params["startDateHi"], strftime="%m-%d-%Y"
            )
        except KeyError:
            pass
        self.url = url
        self.query_params = query_params


@resource.register(r"https://www.waterqualitydata.us/data/Result/search", priority=17)
def resource_epa_csv(uri, **kwargs):
    return EPA_CSV(uri, **kwargs)


# Function to convert from EPA type to pd.DataFrame
@convert.register(pd.DataFrame, EPA_CSV)
def epa_csv_to_df(data, **kwargs):
    req = requests.get(data.url, params=data.query_params)
    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(req.url)
    req.raise_for_status()

    ndf = pd.read_csv(BytesIO(req.content))
    return ndf


if __name__ == "__main__":
    r = resource(
        r"https://www.waterqualitydata.us/data/Result/search",
        characteristicName="Caffeine",
        bBox="-92.8,44.2,-88.9,46.0",
        startDateLo="10-01-2006",
        mimeType="csv",
    )

    as_df = odo(r, pd.DataFrame)
    print("Caffeine")
    print(as_df)
