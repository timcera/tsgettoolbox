
import time
import logging
import os

from odo import odo, resource, convert
import pandas as pd
from requests import Request, Session
from requests.utils import unquote
from requests.exceptions import HTTPError

from tsgettoolbox import utils
from tstoolbox import tsutils

# ncdc_cdo


class ncdc_cdo_json(object):
    def __init__(self, url, **query_params):
        self.url = url
        self.query_params = query_params
        self.query_params['limit'] = 1000
        self.query_params['units'] = 'metric'


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

    sdate = pd.datetime(1900, 1, 1)
    td = pd.datetime.today()
    edate = pd.datetime(td.year, td.month, td.day) + pd.Timedelta(days=1)
    if 'NORMAL_' in data.query_params['datasetid']:
        # All the NORMAL_* datasets must have a startdate/endate of
        # 2010-01-01/2010-12-31
        sdate = pd.datetime(2010, 1, 1)
        edate = pd.datetime(2010, 12, 31)
        delta = pd.Timedelta(days=367)
    elif 'stationid' in data.query_params:
        # Get startdate and/or enddate information
        s = Session()
        ireq = Request('GET',
                       r'http://www.ncdc.noaa.gov/cdo-web/api/v2/stations/{0}'.format(
                           data.query_params['stationid']),
                       headers=headers)
        prepped = ireq.prepare()
        dreq = s.send(prepped)

        sdate = pd.to_datetime(dreq.json()['mindate'])
        edate = pd.to_datetime(dreq.json()['maxdate'])

        if 'startdate' in data.query_params:
            tdate = tsutils.parsedate(data.query_params['startdate'])
            if tdate > sdate:
                sdate = tdate

        if 'enddate' in data.query_params:
            tdate = tsutils.parsedate(data.query_params['enddate'])
            if tdate < edate:
                edate = tdate
        delta = pd.Timedelta(days=365)
    else:
        delta = pd.Timedelta(days=106751)

    if sdate >= edate:
        raise ValueError("""
*
*   The startdate of {0} is greater than, or equal to, the enddate of {1}.
*
""".format(sdate, edate))

    df = pd.DataFrame()

    testdate = sdate
    while testdate < edate:
        time.sleep(1)

        data.query_params['startdate'] = testdate.strftime('%Y-%m-%d')

        testdate = testdate + delta
        if testdate > edate:
            testdate = edate

        data.query_params['enddate'] = testdate.strftime('%Y-%m-%d')

        s = Session()
        ireq = Request('GET',
                       data.url,
                       params=data.query_params,
                       headers=headers)
        prepped = ireq.prepare()
        prepped.url = unquote(prepped.url)
        if os.path.exists('debug_tsgettoolbox'):
            logging.warning(prepped.url)
        req = s.send(prepped)
        try:
            req.raise_for_status()
        except HTTPError:
            continue

        if len(req.content) == 0:
            continue

        try:
            tdf = pd.io.json.json_normalize(req.json()['results'])
        except KeyError:
            continue

        df = df.append(tdf)

    if len(df) == 0:
        if 'NORMAL_' in data.query_params['datasetid']:
            raise ValueError("""
*
*   No normalized statistics available for station {0}
*
""".format(data.query_params['stationid']))
        else:
            raise ValueError("""
*
*   No data within {0} and {1}.
*   There should be data between {2} and {3}.
*
""".format(data.query_params['startdate'],
                data.query_params['enddate'],
                pd.to_datetime(dreq.json()['mindate']),
                pd.to_datetime(dreq.json()['maxdate'])))

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
    # http://www.ncdc.noaa.gov/cdo-web/api/v2/data?
    #  datasetid=PRECIP_15&
    #  stationid=COOP:010008&
    #  units=metric&startdate=2010-05-01&enddate=2010-05-31
    r = resource(
        r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        startdate='2010-05-01',
        enddate='2010-05-31',
        stationid='COOP:010008',
        datasetid='PRECIP_15',
    )
    as_df = odo(r, pd.DataFrame)
    print(as_df)
    mardi = [
        # ['GHCND', 'GHCND:AE000041196'],
        ['GHCND', 'GHCND:USR0000GCOO'],
        ['PRECIP_HLY', 'COOP:087440'],
        ['PRECIP_15', 'COOP:087440'],
        # ['ANNUAL', 'GHCND:US1FLAL0004'],
        ['GHCNDMS', 'GHCND:US1FLAL0004'],
        ['GSOM', 'GHCND:US1FLAL0004'],
        ['GSOY', 'GHCND:USW00012816'],
        # ['NORMAL_ANN', 'GHCND:USC00083322'],
        ['NORMAL_HLY', 'GHCND:USW00013889'],
        ['NORMAL_DLY', 'GHCND:USC00084731'],
        ['NORMAL_MLY', 'GHCND:USC00086618'],
        # ['NEXRAD3', 'NEXRAD:KJAX'],
        # ['NEXRAD2', 'NEXRAD:KJAX'],
    ]
    for did, sid, in mardi:
        startdate = '2016-01-01'
        enddate = '2003-01-01'
        if 'NEXRAD' in did:
            startdate = '2000-01-01'
        if 'PRECIP_' in did:
            startdate = '2013-01-01'

        r = resource(
            r'http://www.ncdc.noaa.gov/cdo-web/api/v2/data',
            startdate=startdate,
            stationid=sid,
            datasetid=did,
        )

        as_df = odo(r, pd.DataFrame)
        print(did)
        print(as_df)

    for did, _ in mardi:
        r = resource(
            r'http://www.ncdc.noaa.gov/cdo-web/api/v2/datatypes',
            startdate='1901-01-01',
            enddate='2016-01-01',
            datasetid=did,
        )

        as_df = odo(r, pd.DataFrame)
        as_df.to_csv('{0}.csv'.format(did))
