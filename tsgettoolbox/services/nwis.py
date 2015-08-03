
import datetime
from collections import defaultdict

from odo import odo, resource, convert
import pandas as pd
import requests


# USGS

class USGS_WML(object):
    def __init__(self, url, **query_params):
        # Need to enforce waterml format
        query_params['format'] = 'waterml,1.1'
        if 'gwlevels' in url:
            query_params['format'] = 'waterml,1.2'
        self.url = url
        self.query_params = query_params

# Can add gwlevels once can parse WML 2.0
#@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/gwlevels/.*', priority=17)
# Function to make `resource` know about the new USGS iv type.
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/dv/.*', priority=17)
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/iv/.*', priority=17)
def resource_usgs(uri, **kwargs):
    return USGS_WML(uri, **kwargs)

# Function to convert from USGS type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_WML)
def usgs_wml_to_df(data, **kwargs):
    from owslib.waterml.wml11 import WaterML_1_1 as wml

    req = requests.get(data.url, params=data.query_params)
    req.raise_for_status()

    variables = wml(req.content).response

    ndf = pd.DataFrame()
    for var in variables.time_series:
        # I don't want the last part of the name which indicates sampling
        # interval
        name = '-'.join(var.name.split(':')[:-1])

        # Extract datetimes and values from wml.
        dt = []
        val = []
        for ndt, nval in var.values[0].get_date_values():
            dt.append(ndt)
            try:
                val.append(int(nval))
            except ValueError:
                val.append(float(nval))

        # Create DataFrame
        ndf = ndf.join(pd.DataFrame(val, index=dt, columns=[name]),
                       how='outer')
    ndf.index.name = 'Datetime'
    return ndf

if __name__ == '__main__':
    #r = resource(
    #    r'http://waterservices.usgs.gov/nwis/gwlevels/',
    #    sites='375907091432201',
    #    startDT='2015-07-01',
    #    endDT='2015-07-30'
    #    )
    #
    #as_df = odo(r, pd.DataFrame)
    #print('USGS_gwlevels')
    #print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/iv/',
        sites='02325000',
        startDT='2015-07-01',
        endDT='2015-07-30'
        )

    as_df = odo(r, pd.DataFrame)
    print('USGS_IV')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/dv/',
        sites='02325000',
        startDT='2015-07-01',
        endDT='2015-07-30'
        )

    as_df = odo(r, pd.DataFrame)
    print('USGS_DV')
    print(as_df)

