
import logging
from io import BytesIO
import os

from odo import odo, resource, convert
import pandas as pd
import requests

from tstoolbox import tsutils

_units_map = {
    'NLDAS:NLDAS_FORA0125_H.002:APCPsfc':
        ['Precipitation hourly total',          'kg/m^2'],
    'NLDAS:NLDAS_FORA0125_H.002:DLWRFsfc':
        ['Surface DW longwave radiation flux',  'W/m^2'],
    'NLDAS:NLDAS_FORA0125_H.002:DSWRFsfc':
        ['Surface DW shortwave radiation flux', 'W/m^2'],
    'NLDAS:NLDAS_FORA0125_H.002:PEVAPsfc':
        ['Potential evaporation',               'kg/m^2'],
    'NLDAS:NLDAS_FORA0125_H.002:SPFH2m':
        ['2-m above ground specific humidity',  'kg/kg'],
    'NLDAS:NLDAS_FORA0125_H.002:TMP2m':
        ['2-m above ground temperature',        'K'],
    'NLDAS:NLDAS_FORA0125_H.002:UGRD10m':
        ['10-m above ground zonal wind',        'm/s'],
    'NLDAS:NLDAS_FORA0125_H.002:VGRD10m':
        ['10-m above ground meridional wind',   'm/s'],
    'NLDAS:NLDAS_NOAH0125_H.002:EVPsfc':
        ['Total evapotranspiration',            'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:GFLUXsfc':
        ['Ground heat flux',                    'w/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:LHTFLsfc':
        ['Latent heat flux',                    'w/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SHTFLsfc':
        ['Sensible heat flux',                  'w/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SSRUNsfc':
        ['Surface runoff (non-infiltrating)',   'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:BGRIUNdfc':
        ['Subsurface runoff (baseflow)',        'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SOILM0-10cm':
        ['0-10 cm soil moisture content',       'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SOILM0-100cm':
        ['0-100 cm soil moisture content',      'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SOILM0-200cm':
        ['0-200 cm soil moisture content',      'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SOILM10-40cm':
        ['10-40 cm soil moisture content',      'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SOILM40-100cm':
        ['40-100 cm soil moisture content',     'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:SOILM100-200cm':
        ['100-200 cm soil moisture content',    'kg/m^2'],
    'NLDAS:NLDAS_NOAH0125_H.002:TSOIL0-10cm':
        ['0-10 cm soil temperature',            'K'],
    'GLDAS:GLDAS_NOAH025_3H.001:Evap':
        ['Evapotranspiration',                  'kg/m^2/s'],
    'GLDAS:GLDAS_NOAH025_3H.001:precip':
        ['Precipitation rate',                  'kg/m^s/hr'],
    'GLDAS:GLDAS_NOAH025_3H.001:Rainf':
        ['Rain rate',                           'kg/m^2/s'],
    'GLDAS:GLDAS_NOAH025_3H.001:Snowf':
        ['Snow rate',                           'kg/m^2/s'],
    'GLDAS:GLDAS_NOAH025_3H.001:Qs':
        ['Surface Runoff',                      'kg/m^2/s'],
    'GLDAS:GLDAS_NOAH025_3H.001:Qsb':
        ['Subsurface Runoff',                   'kg/m^2/s'],
    'GLDAS:GLDAS_NOAH025_3H.001:SOILM0-100cm':
        ['0-100 cm top 1 meter soil moisture content', 'kg/m^2'],
    'GLDAS:GLDAS_NOAH025_3H.001:SOILM0-10cm':
        ['0-10 cm layer 1 soil moisture content',      'kg/m^2'],
    'GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm':
        ['10-40 cm layer 2 soil moisture content',     'kg/m^2'],
    'GLDAS:GLDAS_NOAH025_3H.001:SOILM40-100cm':
        ['40-100 cm layer 3 soil moisture content',    'kg/m^2'],
    'GLDAS:GLDAS_NOAH025_3H.001:Tair':
        ['Near surface air temperature',               'K'],
    'GLDAS:GLDAS_NOAH025_3H.001:TSOIL0-10cm':
        ['Average layer 1 soil temperature',           'K'],
    'GLDAS:GLDAS_NOAH025_3H.001:Wind':
        ['Near surface wind magnitude',                'm/s'],
}

# LDAS


class LDAS(object):
    def __init__(self, url, **query_params):
        query_params['type'] = 'asc2'
        self.url = url
        self.query_params = query_params
        self.query_params['startDate'] = tsutils.parsedate(
            self.query_params['startDate'], strftime='%Y-%m-%dT%H')
        self.query_params['endDate'] = tsutils.parsedate(
            self.query_params['endDate'], strftime='%Y-%m-%dT%H')

# Function to make `resource` know about the new Daymet type.
# http://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi?variable=GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm&location=GEOM:POINT%28-99.875,%2031.125%29&startDate=2010-06-01T09&endDate=2015-05-04T21&type=asc2
# https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi?variable=NLDAS:NLDAS_FORA0125_H.002:APCPsfc&location=NLDAS:X304-Y071&startDate=2015-01-01T00&endDate=2015-06-20T23&type=asc2

@resource.register(r'https://hydro1\.gesdisc\.eosdis\.nasa\.gov/daac-bin/access/timeseries\.cgi.*', priority=17)
def resource_ldas(uri, **kwargs):
    return LDAS(uri, **kwargs)


def _parse_ldas_dates(date, hour):
    try:
        return pd.to_datetime(date) + pd.to_timedelta(pd.np.int(hour[:-1]), 'h')
    except (TypeError, ValueError):
        return pd.NaT

# Function to convert from LDAS type to pd.DataFrame


@convert.register(pd.DataFrame, LDAS)
def ldas_to_df(data, **kwargs):
    req = requests.get(data.url,
                       params=data.query_params)
    if os.path.exists('debug_tsgettoolbox'):
        logging.warning(req.url)
    req.raise_for_status()

    df = pd.read_table(BytesIO(req.content),
                       skiprows=40,
                       header=None,
                       index_col=0,
                       date_parser=_parse_ldas_dates,
                       parse_dates=[[0, 1]],
                       delim_whitespace=True)
    df.drop(df.index[-1], inplace=True)
    variable_name = data.query_params['variable'].split(':')[-1]
    unit = _units_map[data.query_params['variable']][1]
    df.columns = ['{0}:{1}'.format(variable_name, unit)]
    df.index.name = 'Datetime-UTC'
    return df.tz_localize('UTC')


if __name__ == '__main__':
    # ?variable=GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm&
    # location=GEOM:POINT%28-99.875,%2031.125%29&
    # startDate=2010-06-01T09&endDate=2015-05-04T21&type=asc2
    r = resource(
        r'https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi',
        variable='GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm',
        location='GEOM:POINT(-99.875, 31.125)',
        startDate='2010-06-01T09',
        endDate='2015-05-04T21'
    )

    as_df = odo(r, pd.DataFrame)
    print('LDAS')
    print(as_df)

    r = resource(
        r'https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi',
        variable='GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm',
        location='GEOM:POINT(104.2, 35.86)',
        startDate='2016-01-01T00',
        endDate='2016-12-01T00'
    )

    as_df = odo(r, pd.DataFrame)
    print('LDAS TEST')
    print(as_df)

    r = resource(
        r'https://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/access/timeseries.cgi',
        variable='GLDAS:GLDAS_NOAH025_3H.001:SOILM10-40cm',
        location='GEOM:POINT(104.2, 35.86)',
        startDate='5 years ago',
        endDate='4 years ago'
    )

    as_df = odo(r, pd.DataFrame)
    print('LDAS TEST')
    print(as_df)
