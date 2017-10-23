
import logging
import os

from odo import odo, resource, convert
import pandas as pd
import requests

from tstoolbox import tsutils
from tsgettoolbox import utils

# darksky.net


class darksky_net_json(object):
    def __init__(self, url, **query_params):
        self.url = url
        self.url_params = {}
        self.url_params['latitude'] = query_params.pop('latitude')
        self.url_params['longitude'] = query_params.pop('longitude')
        self.url_params['time'] = tsutils.parsedate(query_params.pop('time'),
                                                    strftime='%Y-%m-%dT%H:%M:%S')
        self.include_db = query_params.pop('database')
        all_dbs = ['currently', 'minutely',
                   'hourly', 'daily', 'alerts', 'flags']
        all_dbs.remove(self.include_db)
        query_params['exclude'] = ','.join(all_dbs)
        self.query_params = query_params


@resource.register(r'https://api\.darksky\.net/forecast.*', priority=17)
def resource_darksky_net(uri, **kwargs):
    return darksky_net_json(uri, **kwargs)

# Function to convert from darksky_io_json type to pd.DataFrame


@convert.register(pd.DataFrame, darksky_net_json)
def darksky_net_json_to_df(data, **kwargs):
    # Read in API key
    api_key = utils.read_api_key('darksky.net')

    urlvar = '{0},{1}'.format(data.url_params['latitude'],
                              data.url_params['longitude'])

    time_zone_name = 'LST'
    if data.url_params['time'] is not None:
        time_zone_name = pd.to_datetime(data.url_params['time']).tz
        if time_zone_name is None:
            time_zone_name = 'LST'
        urlvar = urlvar + ',{0}'.format(data.url_params['time'])

    req = requests.get('/'.join([data.url,
                                 api_key,
                                 urlvar]),
                       data.query_params)

    if os.path.exists('debug_tsgettoolbox'):
        logging.warning(req.url)
    req.raise_for_status()

    try:
        ndfj = pd.read_json(req.content, orient='index')
    except ValueError:
        return pd.DataFrame()

    if isinstance(ndfj.ix[0, 0], dict):
        ndfj.ix[0, 0] = [ndfj.ix[0, 0]]

    ndfj = pd.DataFrame(ndfj.ix[data.include_db, :])
    ndfj = ndfj.transpose()

    ndfj.dropna(inplace=True, how='all')

    if data.include_db in ['minutely', 'hourly', 'daily']:
        ndfj = pd.DataFrame(ndfj.ix[data.include_db, 'data'])
    elif data.include_db in ['alerts']:
        ndfj = pd.DataFrame(ndfj.ix[data.include_db, 0])

    if data.include_db != 'flags':
        ndfj.index = pd.to_datetime(ndfj['time'], unit='s')
        ndfj.drop('time', axis=1, inplace=True)
        ndfj.sort_index(inplace=True)

    for datecols in ['apparentTemperatureMinTime',
                     'apparentTemperatureMaxTime',
                     'precipIntensityMaxTime',
                     'sunriseTime',
                     'sunsetTime',
                     'temperatureMaxTime',
                     'temperatureMinTime'
                     ]:
        if datecols in ndfj.columns:
            ndfj[datecols] = pd.to_datetime(ndfj[datecols], unit='s')

    if time_zone_name == 'UTC':
        ndfj = ndfj.tz_localize('UTC')
    ndfj.index.name = 'Datetime-{0}'.format(time_zone_name)
    return ndfj


if __name__ == '__main__':
    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='currently',
        time='2020-01-01T01:00:00',
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net currently')
    print(as_df.head())

    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='minutely',
        time=None,
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net minutely')
    print(as_df.head())

    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='hourly',
        time=None,
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net hourly')
    print(as_df.head())

    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='daily',
        time=None,
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net daily')
    print(as_df.head())

    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='alerts',
        time=None,
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net alerts')
    print(as_df.head())

    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='flags',
        time=None,
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net flags')
    print(as_df.head())

    r = resource(
        r'https://api.darksky.net/forecast',
        latitude=28.45,
        longitude=-81.34,
        database='currently',
        time='yesterday',
    )

    as_df = odo(r, pd.DataFrame)
    print('darksky.net flags')
    print(as_df.head())
