
from __future__ import print_function

import logging
import os
from io import BytesIO

from odo import odo, resource, convert
import pandas as pd
import requests

from tstoolbox import tsutils

# USGS

# parameter_cd	parameter_group_nm	parameter_nm	casrn	srsname	parameter_units
pmcodes = pd.read_csv(os.path.join(os.path.dirname(__file__), 'pmcodes.dat'),
                      comment='#',
                      header=0,
                      sep='\t',
                      dtype={0: str})
pmcodes.set_index('parameter_cd', inplace=True)

# IV
# agency_cd site_no datetime tz_cd 30725_00060 30725_00060_cd 196788_00065 196788_00065_cd
#
# DV
# agency_cd site_no datetime       68479_00010_00001 68479_00010_00001_cd 68482_00010_00001 68482_00010_00001_cd
#
# STAT
# agency_cd site_no                station_nm site_tp_cd dec_lat_va dec_long_va coord_acy_cd dec_coord_datum_cd alt_va alt_acy_va alt_datum_cd huc_cd
#
# GWLEVELS
# agency_cd site_no                site_tp_cd lev_dt lev_tm lev_tz_cd lev_va sl_lev_va sl_datum_cd lev_status_cd lev_agency_cd lev_dt_acy_cd lev_acy_cd lev_src_cd lev_meth_cd lev_age_cd
#
# STATS
# agency_cd site_no                parameter_cd ts_id loc_web_ds month_nu day_nu begin_yr end_yr count_nu max_va_yr max_va min_va_yr min_va mean_va p05_va p10_va p20_va p25_va p50_va p75_va p80_va p90_va p95_va


def _read_rdb(data):
    req = requests.get(data.url,
                       params=data.query_params)
    if os.path.exists('debug_tsgettoolbox'):
        logging.warning(req.url)
    req.raise_for_status()

    if '/iv/' in data.url or '/dv/' in data.url:
        # iv and dv results are stacked, a table for each site.  Have to split
        # the overall req.content into discrete tables for pd.read_csv to work.
        list_of_sublists = list()
        n = 0
        a_list = req.content.splitlines()
        for i, elt in enumerate(a_list):
            if i and elt[:9] == b'agency_cd':
                list_of_sublists.append(a_list[n:i])
                n = i
        list_of_sublists.append(a_list[n:])

        ndf = pd.DataFrame()
        for site in list_of_sublists:
            try:
                adf = pd.read_csv(BytesIO(b'\n'.join(site)),
                                  comment='#',
                                  header=[0, 1],
                                  sep='\t')
            except pd.errors.EmptyDataError:
                continue

            adf.columns = [i[0] for i in adf.columns]

            test_cnames = []
            not_ts = []
            for cname in adf.columns:
                words = cname.split("_")
                try:
                    _ = int(words[0])
                    if "cd" == words[-1]:
                        test_cnames.append(cname)
                    else:
                        test_cnames.append(cname + ":{0}".format(
                            pmcodes.loc[words[1], 'parameter_units']))
                except ValueError:
                    test_cnames.append(cname)
                    not_ts.append(cname)

            adf.columns = test_cnames
            adf.set_index(not_ts, inplace=True)

            if len(ndf) == 0:
                ndf = adf
            else:
                ndf = ndf.join(adf, how="outer")

        ndf.reset_index(inplace=True)
    else:
        ndf = pd.read_csv(BytesIO(req.content),
                          comment='#',
                          header=[0, 1],
                          sep='\t')
        ndf.columns = [i[0] for i in ndf.columns]
    return ndf



def _make_nice_names(ndf):
    nnames = []
    for col in ndf.columns.values:
        strung = [str(i) for i in col]
        nnames.append('_'.join(reversed(strung)).strip())
    return nnames


tzmap = {
    'EST': 'America/New_York',
    'EDT': 'America/New_York',
    'CST': 'America/Chicago',
    'CDT': 'America/Chicago',
    'MST': 'America/Denver',
    'MDT': 'America/Denver',
    'PST': 'America/Los_Angeles',
    'PDT': 'America/Los_Angeles',
}


def normalize_tz(row, tz_cd):
    try:
        return row['Datetime'].tz_localize(tzmap[row[tz_cd]])
    except KeyError:
        return row['Datetime']


class USGS_IV_DV_RDB(object):
    def __init__(self, url, **query_params):
        # Need to enforce RDB format
        query_params['format'] = 'rdb'
        query_params['startDT'] = tsutils.parsedate(query_params['startDT'],
                                                    strftime='%Y-%m-%d')
        query_params['endDT'] = tsutils.parsedate(query_params['endDT'],
                                                  strftime='%Y-%m-%d')

        self.includeCodes = True
        if 'includeCodes' in query_params:
            self.includeCodes = query_params.pop('includeCodes')

        self.url = url
        self.query_params = query_params


# Function to make `resource` know about the new USGS iv type.
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/dv/.*',
                   priority=17)
@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/iv/.*',
                   priority=17)
def resource_usgs_iv_dv_rdb(uri, **kwargs):
    return USGS_IV_DV_RDB(uri, **kwargs)


# Function to convert from USGS RDB type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_IV_DV_RDB)
def usgs_iv_dv_rdb_to_df(data, **kwargs):
    ndf = _read_rdb(data)
    ndf['Datetime'] = pd.to_datetime(ndf['datetime'])
    ndf.drop('datetime',
             axis='columns',
             inplace=True)
    if 'tz_cd' in ndf.columns:
        ndf['Datetime'] = ndf.apply(normalize_tz,
                                    args=('tz_cd',),
                                    axis=1)
        ndf.drop('tz_cd',
                 axis='columns',
                 inplace=True)

    ndf.set_index(['agency_cd',
                   'site_no',
                   'Datetime'],
                  inplace=True)
    ndf = ndf.unstack(level=['site_no',
                             'agency_cd'])

    ndf.columns = _make_nice_names(ndf)

    if data.includeCodes is False:
        ndf.drop([i for i in ndf.columns if i[-3:] == '_cd'],
                 axis='columns',
                 inplace=True)
    return ndf


class USGS_STAT_RDB(object):
    def __init__(self, url, **query_params):

        words = query_params['sites'].split(",")
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
def resource_usgs_stat_rdb(uri, **kwargs):
    return USGS_STAT_RDB(uri, **kwargs)


# Function to convert from USGS STAT_RDB type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_STAT_RDB)
def usgs_stat_rdb_to_df(data, **kwargs):
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

    ndf.columns = _make_nice_names(ndf)

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


class USGS_GWLEVELS_RDB(object):
    def __init__(self, url, **query_params):

        # Need to enforce rdb format
        query_params['format'] = 'rdb'

        self.url = url
        self.query_params = query_params


@resource.register(r'http(s)?://waterservices\.usgs\.gov/nwis/gwlevels/.*',
                   priority=17)
def resource_usgs_gwlevels_rdb(uri, **kwargs):
    return USGS_GWLEVELS_RDB(uri, **kwargs)


# Function to convert from USGS RDB type to pd.DataFrame
@convert.register(pd.DataFrame, USGS_GWLEVELS_RDB)
def usgs_gwlevels_rdb(data, **kwargs):
    ndf = _read_rdb(data)
    # lev_dt    lev_tm  lev_tz_cd
    ndf['Datetime'] = pd.to_datetime(ndf['lev_dt'] +
                                     "T" +
                                     ndf['lev_tm'],
                                     errors='coerce')
    mask = pd.isnull(ndf['Datetime'])
    ndf.loc[mask, 'Datetime'] = pd.to_datetime(ndf.loc[mask, 'lev_dt'],
                                               errors='coerce')
    ndf['Datetime'] = ndf.apply(normalize_tz,
                                args=('lev_tz_cd',),
                                axis=1)
    ndf.set_index(['Datetime'],
                  inplace=True)
    try:
        ndf.index.name = 'Datetime:{0}'.format(ndf.index.tz)
    except AttributeError:
        ndf.index.name = 'Datetime'
    ndf.drop(['lev_dt',
              'lev_tm',
              'lev_tz_cd',
              'site_no'],
             axis=1,
             inplace=True)
    return ndf


if __name__ == '__main__':
    r = resource(
        r'http://waterservices.usgs.gov/nwis/gwlevels/',
        sites='375907091432201',
        startDT='2017-01-01',
        endDT='2017-12-30'
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_GWLEVELS single')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/gwlevels/',
        hucs='03110201',
        startDT='2017-01-01',
        endDT='2017-12-30'
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_GWLEVELS multiple')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/iv/',
        sites='02325000',
        startDT='2015-07-01',
        endDT='2015-07-30'
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_IV single')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/iv/',
        sites='02325000,02239501',
        startDT='2015-07-01',
        endDT='2015-07-30'
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_IV multiple')
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
        r'http://waterservices.usgs.gov/nwis/dv/',
        sites='02325000,02239501',
        startDT='2015-07-01',
        endDT='2015-07-30'
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_DV multiple')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='02325000',
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_DAILY_STAT single')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='02325000,02239501',
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_DAILY_STAT multiple')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='01646500',
        statReportType='monthly',
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_MONTHLY_STAT single')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='02325000,01646500',
        statReportType='monthly',
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_MONTHLY_STAT multiple')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='01646500',
        statReportType='annual',
        statYearType='water',
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_ANNUAL_STAT single')
    print(as_df)

    r = resource(
        r'http://waterservices.usgs.gov/nwis/stat/',
        sites='01646500,02239501',
        statReportType='annual',
        statYearType='water',
    )
    as_df = odo(r, pd.DataFrame)
    print('USGS_ANNUAL_STAT multple')
    print(as_df)
