
import datetime
import logging
import os

from odo import odo, resource, convert
import pandas as pd

from tstoolbox import tsutils

try:
    import urllib.parse as urlp
except ImportError:
    import urllib as urlp

_units_map = {
    'tmax': 'deg_C',
    'tmin': 'deg_C',
    'srad': 'W/m2',
    'vp': 'Pa',
    'swe': 'kg/m2',
    'prcp': 'mm',
    'dayl': 's',
}

# Daymet

# pd.read_csv('http://daymet.ornl.gov/data/send/saveData?measuredParams=tmax,tmin,prcp&lat=43.1&lon=-85.3&year=2000,2001',
# skiprows=7,
# date_parser=testp,
# index_col=0,
# parse_dates=[[0,1]])


class Daymet(object):
    def __init__(self, url, **query_params):
        avail_params = ['tmax', 'tmin', 'srad', 'vp', 'swe', 'prcp', 'dayl']
        params = {
            'measureParams': None,
            'year': None,
        }
        params.update(query_params)
        if params['measuredParams'] is None:
            params['measuredParams'] = ','.join(['tmax',
                                                 'tmin',
                                                 'srad',
                                                 'vp',
                                                 'swe',
                                                 'prcp',
                                                 'dayl',
                                                 ])
        else:
            for testparams in params['measuredParams'].split(','):
                if testparams not in avail_params:
                    raise ValueError('''
*
*   The measuredParams must be 'tmax', 'tmin', 'srad', 'vp', 'swe', 'prcp',
*   and 'dayl'.  You supplied {0}.
*
'''.format(testparams))

        last_year = datetime.datetime.now().year - 1
        if params['year'] is None:
            params['year'] = ','.join([str(i)
                                       for i in range(1980, last_year + 1)])
        else:
            accumyear = []
            for testyear in params['year'].split(','):
                try:
                    iyear = int(tsutils.parsedate(testyear,
                                                  strftime='%Y'))
                    accumyear.append(iyear)
                except ValueError:
                    raise ValueError('''
*
*   The year= option must contain a comma separated list of integers.  You
*   supplied {0}.
*
'''.format(testyear))
                if iyear < 1980 or iyear > last_year:
                    raise ValueError('''
*
*   The year= option must contain values from 1980 up to and including the last
*   calendar year.  You supplied {0}.
*
'''.format(iyear))

            params['year'] = ",".join([str(i) for i in accumyear])

        self.url = url
        self.query_params = params

# Function to make `resource` know about the new Daymet type.


@resource.register(r'http(s)?://daymet\.ornl\.gov.*', priority=17)
def resource_daymet(uri, **kwargs):
    return Daymet(uri, **kwargs)


def _daymet_date_parser(year, doy):
    return pd.to_datetime(year) + pd.to_timedelta(pd.np.int(doy), 'D') - pd.to_timedelta(1, 'D')

# Function to convert from Daymet type to pd.DataFrame


@convert.register(pd.DataFrame, Daymet)
def daymet_to_df(data, **kwargs):
    req = urlp.unquote('{}?{}'.format(data.url,
                                      urlp.urlencode(data.query_params)))
    if os.path.exists('debug_tsgettoolbox'):
        logging.warning(req)
    df = pd.read_csv(req,
                     skiprows=7,
                     sep=",",
                     date_parser=_daymet_date_parser,
                     header=0,
                     index_col=0,
                     skipinitialspace=True,
                     parse_dates=[[0, 1]])
    df.columns = ['Daymet-{0}'.format(i.replace(' ', '_')) for i in df.columns]
    df.index.name = 'Datetime'
    return df


if __name__ == '__main__':
    r = resource(
        r'http://daymet.ornl.gov/data/send/saveData',
        measuredParams='tmax,tmin',
        lat=43.1,
        lon=-85.2,
        year='2000,2001'
    )

    as_df = odo(r, pd.DataFrame)
    print('Daymet')
    print(as_df)

    r = resource(
        r'http://daymet.ornl.gov/data/send/saveData',
        measuredParams='tmax,tmin',
        lat=43.1,
        lon=-85.2,
        year='3 years ago,2 years ago'
    )

    as_df = odo(r, pd.DataFrame)
    print('Daymet')
    print(as_df)
