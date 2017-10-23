
import logging
from io import BytesIO
import os

from odo import odo, resource, convert
import pandas as pd
import requests

from tstoolbox import tsutils

# http://sdf.ndbc.noaa.gov/sos/server.php?
#     request=GetObservation&
#     service=SOS&
#     version=1.0.0&
#     offering=urn:ndbc:station:wmo:41012&
#     observedproperty=air_pressure_at_sea_level&
#     responseformat=text/csv&
#     eventtime=2011-03-01T00:00Z/2011-03-02T00:00Z


class NDBC(object):
    def __init__(self, url, **query_params):
        query_params['request'] = 'GetObservation'
        query_params['service'] = 'SOS'
        query_params['version'] = '1.0.0'
        query_params['responseformat'] = 'text/csv'

        query_params['offering'] = 'urn:ioos:station:wmo:{0}'.format(
            query_params['station'].lower())
        query_params.pop('station')

        if query_params['observedproperty'] is None:
            query_params.pop('observedproperty')

        self.url = url
        self.query_params = query_params

# Function to make `resource` know about the new NOS type.


@resource.register(r'http://sdf\.ndbc\.noaa\.gov/sos/server\.php.*', priority=17)
def resource_ndbc(uri, **kwargs):
    return NDBC(uri, **kwargs)

# Function to convert from NDBC type to pd.DataFrame


@convert.register(pd.DataFrame, NDBC)
def ndbc_to_df(data, **kwargs):

    oprop = ['air_pressure_at_sea_level',
             'air_temperature',
             'currents',
             'sea_floor_depth_below_sea_surface',
             'sea_water_electrical_conductivity',
             'sea_water_salinity',
             'sea_water_temperature',
             'waves',
             'winds',
             ]
    delta = pd.Timedelta(days=30)

    sdate = tsutils.parsedate(data.query_params.pop('startUTC'))
    edate = tsutils.parsedate(data.query_params.pop('endUTC'))

    df = pd.DataFrame()

    testdate = sdate
    while testdate < edate:
        tsdate = testdate

        testdate = testdate + delta
        if testdate > edate:
            testdate = edate

        data.query_params['eventtime'] = '{0}/{1}'.format(tsdate.strftime('%Y-%m-%dT%H:%MZ'),
                                                          testdate.strftime('%Y-%m-%dT%H:%MZ'))

        req = requests.get(data.url,
                           params=data.query_params)

        if os.path.exists('debug_tsgettoolbox'):
            logging.warning(req.url)
        req.raise_for_status()

        tdf = pd.read_csv(BytesIO(req.content),
                          parse_dates=['date_time'])
        if len(tdf) > 0:
            df = df.append(tdf)

    if len(df) == 0:
        raise ValueError("""
*
*   No data collected/available within this time frame.
*
""")

    for dcols in ['station_id',
                  'sensor_id',
                  'latitude (degree)',
                  'longitude (degree)']:
        df.drop(dcols, axis='columns', inplace=True)

    df = df.pivot_table(columns='depth (m)',
                        index='date_time',
                        values=df.columns.drop('depth (m)'))

    df.dropna(axis='columns', how='all', inplace=True)

    ind = pd.Index(['{0}@{1}m'.format(e[0], e[1])
                    for e in df.columns.tolist()])
    df.columns = ind

    df.index.name = 'Datetime'
    return df


if __name__ == '__main__':
    """
    """

    r = resource(
        r'http://sdf.ndbc.noaa.gov/sos/server.php',
        # observedproperty='air_pressure_at_sea_level',
        observedproperty='currents',
        startUTC='2012-01-01T00:00Z',
        endUTC='2012-04-01:00Z',
        station='41012',
    )

    as_df = odo(r, pd.DataFrame)
    print('NDBC')
    print(as_df)
    as_df.to_csv('file.csv')
