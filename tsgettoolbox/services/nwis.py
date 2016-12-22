
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
def resource_usgs_wml(uri, **kwargs):
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


class USGS_RDB(object):
    def __init__(self, url, **query_params):

        # set defaults.
        for key, val in [['statYearType', 'calendar'],
                         ['missingData', 'off'],
                         ['statType', 'all'],
                         ['statReportType', 'daily']
                        ]:
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
    ndf = pd.read_csv(requests.Request(
        'GET',
        data.url,
        params=data.query_params,
        ).prepare().url,
                      comment='#',
                      header=0,
                      sep='\t')
    ndf.drop(ndf.index[0], inplace=True)
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
    print(ndf.columns)
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
