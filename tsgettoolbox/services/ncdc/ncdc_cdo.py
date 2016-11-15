
import time

from odo import odo, resource, convert
import pandas as pd
import requests

from tsgettoolbox import utils

# ncdc_cdo

class ncdc_cdo_json(object):
    def __init__(self, url, **query_params):
        self.url = url
        self.query_params = query_params
        self.query_params['limit'] = 1000

@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/datasets*', priority=17)
@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/datacategories*', priority=17)
@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/datatypes*', priority=17)
@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/locationcategories*', priority=17)
@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/locations*', priority=17)
@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/stations*', priority=17)
@resource.register(r'http://www\.ncdc\.noaa\.gov/cdo-web/api/v2/data/*', priority=17)
def resource_ncdc_cdo(uri, **kwargs):
    return ncdc_cdo_json(uri, **kwargs)

# Function to convert from ncdc_cdo_json type to pd.DataFrame
@convert.register(pd.DataFrame, ncdc_cdo_json)
def ncdc_cdo_json_to_df(data, **kwargs):
    # Read in API key
    api_key = utils.read_api_key('ncdc_cdo')

    headers = {'token': api_key}

    sdate = pd.datetime(1800, 1, 1)
    edate = pd.datetime(2500, 1, 1)
    if 'NORMAL_' in data.query_params['datasetid']:
        # All the NORMAL_* datasets must have a startdate/endate of
        # 2010-01-01/2010-12-31
        sdate = pd.datetime(2010, 1, 1)
        data.query_params['startdate'] = sdate
        edate = pd.datetime(2010, 12, 31)
        data.query_params['enddate'] = edate
    elif 'stationid' in data.query_params:
        # Get startdate and/or enddate information
        dreq = requests.get(
            r'http://www.ncdc.noaa.gov/cdo-web/api/v2/stations/{0}'.format(
                data.query_params['stationid']),
                        headers=headers)
        sdate = pd.to_datetime(dreq.json()['mindate'])
        edate = pd.to_datetime(dreq.json()['maxdate'])

        if 'startdate' in data.query_params:
            tdate = pd.to_datetime(data.query_params['startdate'])
            if tdate > sdate:
                sdate = tdate

        edate = pd.to_datetime(dreq.json()['maxdate'])
        if 'enddate' in data.query_params:
            tdate = pd.to_datetime(data.query_params['enddate'])
            if tdate < edate:
                edate = tdate

    df = pd.DataFrame()

    delta = pd.Timedelta(days=365)

    testdate = sdate
    while testdate < edate:
        data.query_params['startdate'] = testdate.strftime('%Y-%m-%d')

        testdate = testdate + delta
        if testdate > edate:
            testdate = edate

        data.query_params['enddate'] = testdate.strftime('%Y-%m-%d')

        req = requests.get(data.url,
                           data.query_params,
                           headers = headers)
        req.raise_for_status()

        time.sleep(1)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError:
            continue

        try:
            tdf = pd.io.json.json_normalize(req.json()['results'])
        except KeyError:
            continue

        df = df.append(tdf)

    df.drop_duplicates(df.columns, keep='first', inplace=True)

    if 'date' in df.columns:
        fdf = df.pivot(index='date',
                       columns='datatype',
                       values='value')

        df['dt_att'] = df['datatype'] + '_att'
        sdf = df.pivot(index='date',
                       columns='dt_att',
                       values='attributes')

        ndf = fdf.join(sdf)
    else:
        ndf = tdf

    return ndf


if __name__ == '__main__':
    for did, sid, in [
                      ['PRECIP_HLY', 'COOP:087440'],
                      ['GHCND', 'GHCND:AE000041196'],
                      ['PRECIP_15', 'COOP:087440'],
                      #['ANNUAL', 'GHCND:US1FLAL0004'],
                      ['GHCNDMS', 'GHCND:US1FLAL0004'],
                      ['GSOM', 'GHCND:US1FLAL0004'],
                      ['GSOY', 'GHCND:USW00012816'],
                      ['NORMAL_ANN', 'GHCND:USC00083322'],
                      ['NORMAL_HLY', 'GHCND:USW00013889'],
                      ['NORMAL_DLY', 'GHCND:USC00084731'],
                      ['NORMAL_MLY', 'GHCND:USC00086618'],
                      #['NEXRAD3', 'NEXRAD:KJAX'],
                      #['NEXRAD2', 'NEXRAD:KJAX'],
                     ]:

        startdate = '2014-01-01'
        if 'NEXRAD' in did:
            startdate = '2000-01-01'
        if 'PRECIP_' in did:
            startdate = '2013-01-01'

        r = resource(
            r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
            startdate = startdate,
            datasetid = did,
            stationid = sid,
            )

        as_df = odo(r, pd.DataFrame)
        print(did)
        print(as_df)

    for did in ['GHCND',
                'GHCNDMS',
                'GSOM',
                'GSOY',
                'NEXRAD2',
                'NEXRAD3',
                'NORMAL_ANN',
                'NORMAL_DLY',
                'NORMAL_HLY',
                'NORMAL_MLY',
                'PRECIP_15',
                'PRECIP_HLY',
                'ANNUAL',
               ]:
        r = resource(
            r'http://www.ncdc.noaa.gov/cdo-web/api/v2/datatypes',
            startdate = '1900-01-01',
            enddate = '2016-01-01',
            datasetid = did,
            )

        as_df = odo(r, pd.DataFrame)
        as_df.to_csv('{0}.csv'.format(did))

