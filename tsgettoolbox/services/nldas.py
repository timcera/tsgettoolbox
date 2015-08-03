
import datetime
from collections import defaultdict

from odo import odo, resource, convert
import pandas as pd
import requests
from pydap.client import open_url

# nldas

class nldas(object):
    def __init__(self, url, **query_params):
        avail_params = [
                        'apcpsfc',
                        'cape180_0mb',
                        'convfracsfc',
                        'dlwrfsfc',
                        'dswrfsfc',
                        'pevapsfc',
                        'pressfc',
                        'spfh2m',
                        'tmp2m',
                        'ugrd10m',
                        'vgrd10m',
                        ]

        params = {
                  'variables': ','.join(avail_params),
                  }
        params.update(query_params)
        for testparams in params['variables'].split(','):
            if testparams not in avail_params:
                raise ValueError('''
*
*   The variables must be in the set ('apcpsfc', 'cape180_0mb', 'convfracsfc',
*   'dlwrfsfc', 'dswrfsfc', 'pevapsfc', 'pressfc', 'spfh2m', 'tmp2m',
*   'ugrd10m', and 'vgrd10m').  You supplied {0}.
*
'''.format(testparams))
        self.url = url
        self.query_params = params

# Function to make `resource` know about the new nldas type.
@resource.register(r'http://hydro1.sci.gsfc.nasa.gov:80/dods/NLDAS_FORA0125_H.002.*', priority=17)
def resource_nldas(uri, **kwargs):
    return nldas(uri, **kwargs)

def _closest(arr, interpolate):
    return (pd.np.abs(arr - interpolate)).argmin()

def _nldas_date_parser(x):
    year, doy = x.split(' ')
    return pd.to_datetime(year) + pd.to_timedelta(int(doy) - 1, 'D')

# Function to convert from nldas type to pd.DataFrame
@convert.register(pd.DataFrame, nldas)
def nldas_to_df(data, **kwargs):
    lat = data.query_params['lat']
    lon = data.query_params['lon']
    dataset = open_url(data.url)
    lat_idx = _closest(dataset['lat'].data[:], lat)
    lon_idx = _closest(dataset['lon'].data[:], lon)
    df = pd.read_csv(
                     requests.Request(
                         'GET',
                         data.url,
                         params=data.query_params,
                     ).prepare().url,
                     skiprows=7,
                     date_parser=_nldas_date_parser,
                     index_col=0,
                     parse_dates=[[0, 1]])
    df.columns = ['nldas-{0}-{1}'.format(i, _units_map[i]) for i in df.columns]
    df.index.name = 'Datetime'
    return df

if __name__ == '__main__':
    r = resource(
        r'http://nldas.ornl.gov/data/send/saveData',
        measuredParams='tmax,tmin',
        lat=43.1,
        lon=-85.2,
        year='2000,2001'
        )

    as_df = odo(r, pd.DataFrame)
    print('nldas')
    print(as_df)

