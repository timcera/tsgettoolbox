

from __future__ import print_function

import logging
import os
from io import BytesIO

from odo import odo, resource, convert
import pandas as pd
import requests

from tstoolbox import tsutils

# USGS


class USGS_WML(object):
    def __init__(self, url, **query_params):
        # Need to enforce waterml format
        query_params['format'] = 'waterml,1.1'
        if 'gwlevels' in url:
            query_params['format'] = 'waterml,1.2'
        query_params['startDT'] = tsutils.parsedate(query_params['startDT'],
                                                    strftime='%Y-%m-%d')
        query_params['endDT'] = tsutils.parsedate(query_params['endDT'],
                                                  strftime='%Y-%m-%d')
        self.url = url
        self.query_params = query_params


# Can add gwlevels once can parse WML 2.0
# @resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/gwlevels/.*',
#                    priority=17)
# Function to make `resource` know about the new USGS iv type.
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/dv/.*',
                   priority=17)
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/iv/.*',
                   priority=17)
def resource_usgs_wml(uri, **kwargs):
    return USGS_WML(uri, **kwargs)


# Function to convert from USGS type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_WML)
def usgs_wml_to_df(data, **kwargs):
    from owslib.waterml.wml11 import WaterML_1_1 as wml

    req = requests.get(data.url,
                       params=data.query_params)
    if os.path.exists('debug_tsgettoolbox'):
        logging.warning(req.url)
    req.raise_for_status()

    variables = wml(req.content).response

    ndf = pd.DataFrame()
    for var in variables.time_series:
        # Replace the : with -
        name = '-'.join(var.name.split(':'))

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
        ndf = ndf.join(pd.DataFrame(val,
                                    index=dt,
                                    columns=[name]),
                       how='outer',
                       rsuffix='_1')
    ndf.index.name = 'Datetime'
    return ndf


def _read_rdb(data):
    req = requests.get(data.url,
                       params=data.query_params)
    if os.path.exists('debug_tsgettoolbox'):
        logging.warning(req.url)
    req.raise_for_status()

    ndf = pd.read_csv(BytesIO(req.content),
                      comment='#',
                      header=0,
                      sep='\t')
    ndf.drop(ndf.index[0], inplace=True)
    return ndf


class USGS_RDB(object):
    def __init__(self, url, **query_params):

        # set defaults.
        for key, val in [['statYearType', 'calendar'],
                         ['missingData', 'off'],
                         ['statType', 'all'],
                         ['statReportType', 'daily']]:
            try:
                if query_params[key] is None:
                    query_params[key] = val
            except KeyError:
                query_params[key] = val

        # Need to enforce rdb format
        query_params['format'] = 'rdb'

        if query_params['statReportType'] != 'annual':
            query_params['statYearType'] = None
        if query_params['statReportType'] == 'daily':
            query_params['missingData'] = None
        self.url = url
        self.query_params = query_params


# Function to make `resource` know about the new USGS stat type.
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/stat/.*',
                   priority=17)
def resource_usgs_rdb(uri, **kwargs):
    return USGS_RDB(uri, **kwargs)


# Function to convert from USGS RDB type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_RDB)
def usgs_rdb_to_df(data, **kwargs):
    ndf = _read_rdb(data)
    if data.query_params['statReportType'] == 'daily':
        ndf['Datetime'] = ['{0:02d}-{1:02d}'.format(int(i), int(j))
                           for i, j in zip(ndf['month_nu'], ndf['day_nu'])]
        ndf.drop(['month_nu', 'day_nu'], axis=1, inplace=True)
    elif data.query_params['statReportType'] == 'monthly':
        ndf['Datetime'] = pd.to_datetime(['{0}-{1:02d}'.format(i, int(j))
                                          for i, j in zip(ndf['year_nu'],
                                                          ndf['month_nu'])])
        ndf.drop(['year_nu', 'month_nu'], axis=1, inplace=True)
    else:
        if data.query_params['statYearType'] == 'water':
            ndf['Datetime'] = pd.to_datetime(['{0}-10-01'.format(int(i) - 1)
                                              for i in ndf['year_nu']])
        else:
            ndf['Datetime'] = pd.to_datetime(ndf['year_nu'])
        ndf.drop('year_nu', axis=1, inplace=True)
    ndf.sort_values(['agency_cd',
                     'site_no',
                     'parameter_cd',
                     'ts_id',
                     'Datetime'],
                    inplace=True)
    ndf.set_index(['agency_cd',
                   'site_no',
                   'parameter_cd',
                   'ts_id',
                   'Datetime'],
                  inplace=True)
    ndf = ndf.unstack(level=['agency_cd',
                             'site_no',
                             'parameter_cd',
                             'ts_id'])
    ndf = ndf.reorder_levels([1, 2, 3, 4, 0], axis=1)
    ndf.columns = [':'.join(col).strip() for col in ndf.columns.values]
    return ndf


statelookup = {
    1: 'AL',  # Alabama
    2: 'AK',  # Alaska
    4: 'AZ',  # Arizona
    5: 'AR',  # Arkansas
    6: 'CA',  # California
    8: 'CO',  # Colorado
    9: 'CT',  # Connecticut
    10: 'DE',  # Delaware
    11: 'DC',  # District of Columbia
    12: 'FL',  # Florida
    13: 'GA',  # Georgia
    15: 'HI',  # Hawaii
    16: 'ID',  # Idaho
    17: 'IL',  # Illinois
    18: 'IN',  # Indiana
    19: 'IA',  # Iowa
    20: 'KS',  # Kansas
    21: 'KY',  # Kentucky
    22: 'LA',  # Louisiana
    23: 'ME',  # Maine
    24: 'MD',  # Maryland
    25: 'MA',  # Massachusetts
    26: 'MI',  # Michigan
    27: 'MN',  # Minnesota
    28: 'MS',  # Mississippi
    29: 'MO',  # Missouri
    30: 'MT',  # Montana
    31: 'NE',  # Nebraska
    32: 'NV',  # Nevada
    33: 'NH',  # New Hampshire
    34: 'NJ',  # New Jersey
    35: 'NM',  # New Mexico
    36: 'NY',  # New York
    37: 'NC',  # North Carolina
    38: 'ND',  # North Dakota
    39: 'OH',  # Ohio
    40: 'OK',  # Oklahoma
    41: 'OR',  # Oregon
    42: 'PA',  # Pennsylvania
    44: 'RI',  # Rhode Island
    45: 'SC',  # South Carolina
    46: 'SD',  # South Dakota
    47: 'TN',  # Tennessee
    48: 'TX',  # Texas
    49: 'UT',  # Utah
    50: 'VT',  # Vermont
    51: 'VA',  # Virginia
    53: 'WA',  # Washington
    54: 'WV',  # West Virginia
    55: 'WI',  # Wisconsin
    56: 'WY',  # Wyoming
}


class USGS_MEASUREMENTS_PEAK_RDB(object):
    def __init__(self, url, **query_params):

        if 'measurements' in url:
            rdb_format = 'rdb_expanded'
        elif 'peak' in url:
            rdb_format = 'rdb'

        # Need to enforce rdb format
        query_params['format'] = rdb_format
        query_params['agency_cd'] = 'USGS'
        query_params['site_no'] = query_params['sites']
        query_params.pop('sites')

        # Get the state code and insert into URL
        r = odo(resource(r'http://waterservices.usgs.gov/nwis/site/',
                         sites=query_params['site_no']),
                pd.DataFrame)
        try:
            url = url.replace('XX',
                              statelookup[int(r.ix[1,
                                                   u'state_cd'])].lower())
        except KeyError:
            raise ValueError("""
*
*   No field measurements available.  Some states don't have any posted
*   to NWIS.
*
""")

        self.url = url
        self.query_params = query_params


# https://nwis.waterdata.usgs.gov/fl/nwis/measurements?site_no=02315500&agency_cd=USGS&format=rdb_expanded
@resource.register(
    r'http(s)?://nwis\.waterdata\.usgs\.gov/../nwis/measurements.*',
    priority=17)
# https://nwis.waterdata.usgs.gov/fl/nwis/peak?site_no=02315500&agency_cd=USGS&format=rdb_expanded
@resource.register(r'http(s)?://nwis\.waterdata\.usgs\.gov/../nwis/peak.*',
                   priority=17)
def resource_usgs_measurements_peak_rdb(uri, **kwargs):
    return USGS_MEASUREMENTS_PEAK_RDB(uri, **kwargs)


# Function to convert from USGS RDB type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_MEASUREMENTS_PEAK_RDB)
def usgs_measurements_peak_rdb_to_df(data, **kwargs):
    ndf = _read_rdb(data)
    if 'measurements' in data.url:
        dname = 'measurement_dt'
    elif 'peak' in data.url:
        dname = 'peak_dt'
    ndf['Datetime'] = pd.to_datetime(ndf[dname], errors='coerce')
    ndf.set_index(['Datetime'],
                  inplace=True)
    ndf.drop([dname,
              'agency_cd',
              'site_no'],
             axis=1,
             inplace=True)
    return ndf


class USGS_SITE_RDB(object):
    def __init__(self, url, **query_params):

        # Need to enforce rdb format
        query_params['format'] = 'rdb'
        query_params['siteOutput'] = 'expanded'
        query_params['siteStatus'] = 'all'

        self.url = url
        self.query_params = query_params


# https://waterservices.usgs.gov/nwis/site/?format=rdb&sites=01646500&siteOutput=expanded&siteStatus=all
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/site.*',
                   priority=17)
def resource_usgs_site_rdb(uri, **kwargs):
    return USGS_SITE_RDB(uri, **kwargs)


# Function to convert from USGS RDB type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_SITE_RDB)
def usgs_site_rdb_to_df(data, **kwargs):
    ndf = _read_rdb(data)
    return ndf


if __name__ == '__main__':
    # r = resource(
    #     r'http://waterservices.usgs.gov/nwis/gwlevels/',
    #     sites='375907091432201',
    #     startDT='2015-07-01',
    #     endDT='2015-07-30'
    #     )
    #
    # as_df = odo(r, pd.DataFrame)
    # print('USGS_gwlevels')
    # print(as_df)

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

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='02325000',
    )

    as_df = odo(r, pd.DataFrame)
    print('USGS_DAILY_STAT')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='01646500',
        statReportType='monthly',
    )

    as_df = odo(r, pd.DataFrame)
    print('USGS_MONTHLY_STAT')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='01646500',
        statReportType='annual',
        statYearType='water',
    )

    as_df = odo(r, pd.DataFrame)
    print('USGS_ANNUAL_STAT')
    print(as_df)
