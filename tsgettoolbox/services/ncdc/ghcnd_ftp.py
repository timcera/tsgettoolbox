

from odo import odo, resource, convert
import pandas as pd

from tstoolbox import tsutils

# GHCND
# Global Historical Climatology Network - Daily

# pd.read_csv('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/{0}.dly',
# skiprows=7,
# date_parser=testp,
# index_col=0,
# parse_dates=[[0,1]])

class ghcnd(object):
    def __init__(self, url, **query_params):
        params = {
            'station': None,
            'start_date': None,
            'end_date': None,
            }
        params.update(query_params)

        self.url = url
        self.query_params = params

# Function to make `resource` know about the new ghcnd type.
@resource.register(r'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all.*', priority=17)
def resource_ghcnd(uri, **kwargs):
    return ghcnd(uri, **kwargs)

# Function to convert from ghcnd type to pd.DataFrame
@convert.register(pd.DataFrame, ghcnd)
def ghcnd_to_df(data, **kwargs):
    df = pd.read_fwf(data.url + '/' + data.query_params['station'] + '.dly',
                     widths=[11, 4, 2, 4] + [5, 1, 1, 1]*31)
    newcols = ['station', 'year', 'month', 'code']
    for day in list(range(1, 32)):
        for col in ['', 'm', 'q', 's']:
            newcols.append('{0}{1:02}'.format(col, day))
    df.columns = newcols
    codes = ['TMAX',  # Temperature MAX (1/10 degree C)
             'TMIN',  # Temperature MIN (1/10 degree C)
             'PRCP',  # PReCiPitation (tenths of mm)
             'SNOW',  # SNOWfall (mm)
             'SNWD',  # SNoW Depth (mm)
             'ACMC',  # Average cloudiness midnight to midnight from 30-second ceilometer data (percent)
             'ACMH',  # Average cloudiness midnight to midnight from manual observations (percent)
             'ACSC',  # Average cloudiness sunrise to sunset from 30-second ceilometer data (percent)
             'ACSH',  # Average cloudiness sunrise to sunset from manual observations (percent)
             'AWDR',  # Average daily wind direction (degrees)
             'AWND',  # Average daily wind speed (tenths of meters per second)
             'DAEV',  # Number of days included in the multiday evaporation total (MDEV)
             'DAPR',  # Number of days included in the multiday precipiation total (MDPR)
             'DASF',  # Number of days included in the multiday snowfall total (MDSF)
             'DATN',  # Number of days included in the multiday minimum temperature (MDTN)
             'DATX',  # Number of days included in the multiday maximum temperature (MDTX)
             'DAWM',  # Number of days included in the multiday wind movement (MDWM)
             'DWPR',  # Number of days with non-zero precipitation included in multiday precipitation total (MDPR)
             'EVAP',  # Evaporation of water from evaporation pan (tenths of mm)
             'FMTM',  # Time of fastest mile or fastest 1-minute wind (hours and minutes, i.e., HHMM)
             'FRGB',  # Base of frozen ground layer (cm)
             'FRGT',  # Top of frozen ground layer (cm)
             'FRTH',  # Thickness of frozen ground layer (cm)
             'GAHT',  # Difference between river and gauge height (cm)
             'MDEV',  # Multiday evaporation total (tenths of mm; use with DAEV)
             'MDPR',  # Multiday precipitation total (tenths of mm; use with DAPR and DWPR, if available)
             'MDSF',  # Multiday snowfall total
             'MDTN',  # Multiday minimum temperature (tenths of degrees C; use with DATN)
             'MDTX',  # Multiday maximum temperature (tenths of degress C; use with DATX)
             'MDWM',  # Multiday wind movement (km)
             'MNPN',  # Daily minimum temperature of water in an evaporation pan (tenths of degrees C)
             'MXPN',  # Daily maximum temperature of water in an evaporation pan (tenths of degrees C)
             'PGTM',  # Peak gust time (hours and minutes, i.e., HHMM)
             'PSUN',  # Daily percent of possible sunshine (percent)
             'TAVG',  # Average temperature (tenths of degrees C) [Note that TAVG from source 'S' corresponds to an average for the period ending at 2400 UTC rather than local midnight]
             'THIC',  # Thickness of ice on water (tenths of mm)
             'TOBS',  # Temperature at the time of observation (tenths of degrees C)
             'TSUN',  # Daily total sunshine (minutes)
             'WDF1',  # Direction of fastest 1-minute wind (degrees)
             'WDF2',  # Direction of fastest 2-minute wind (degrees)
             'WDF5',  # Direction of fastest 5-second wind (degrees)
             'WDFG',  # Direction of peak wind gust (degrees)
             'WDFI',  # Direction of highest instantaneous wind (degrees)
             'WDFM',  # Fastest mile wind direction (degrees)
             'WDMV',  # 24-hour wind movement (km)
             'WESD',  # Water equivalent of snow on the ground (tenths of mm)
             'WESF',  # Water equivalent of snowfall (tenths of mm)
             'WSF1',  # Fastest 1-minute wind speed (tenths of meters per second)
             'WSF2',  # Fastest 2-minute wind speed (tenths of meters per second)
             'WSF5',  # Fastest 5-second wind speed (tenths of meters per second)
             'WSFG',  # Peak gust wind speed (tenths of meters per second)
             'WSFI',  # Highest instantaneous wind speed (tenths of meters per second)
             'WSFM',  # Fastest mile wind speed (tenths of meters per second)
            ]

    # SN*# = Minimum soil temperature (tenths of degrees C)
    #        where * corresponds to a code
    #        for ground cover and # corresponds to a code for soil
    #        depth.
    #
    #        Ground cover codes include the following:
    #        0 = unknown
    #        1 = grass
    #        2 = fallow
    #        3 = bare ground
    #        4 = brome grass
    #        5 = sod
    #        6 = straw multch
    #        7 = grass muck
    #        8 = bare muck
    #
    #        Depth codes include the following:
    #        1 = 5 cm
    #        2 = 10 cm
    #        3 = 20 cm
    #        4 = 50 cm
    #        5 = 100 cm
    #        6 = 150 cm
    #        7 = 180 cm
    for i in range(9):
        for j in range(1, 8):
            codes.append('SN{0}{1}'.format(i, j))

    # SX*# = Maximum soil temperature (tenths of degrees C)
    #        where * corresponds to a code for ground cover
    #        and # corresponds to a code for soil depth.
    #        See SN*# for ground cover and depth codes.
    for i in range(9):
        for j in range(1, 8):
            codes.append('SX{0}{1}'.format(i, j))

    # WT** = Weather Type where ** has one of the following values:
    #
    #        01 = Fog, ice fog, or freezing fog (may include heavy fog)
    #        02 = Heavy fog or heaving freezing fog (not always distinquished from fog)
    #        03 = Thunder
    #        04 = Ice pellets, sleet, snow pellets, or small hail
    #        05 = Hail (may include small hail)
    #        06 = Glaze or rime
    #        07 = Dust, volcanic ash, blowing dust, blowing sand, or blowing obstruction
    #        08 = Smoke or haze
    #        09 = Blowing or drifting snow
    #        10 = Tornado, waterspout, or funnel cloud
    #        11 = High or damaging winds
    #        12 = Blowing spray
    #        13 = Mist
    #        14 = Drizzle
    #        15 = Freezing drizzle
    #        16 = Rain (may include freezing rain, drizzle, and freezing drizzle)
    #        17 = Freezing rain
    #        18 = Snow, snow pellets, snow grains, or ice crystals
    #        19 = Unknown source of precipitation
    #        21 = Ground fog
    #        22 = Ice fog or freezing fog
    codes.extend(['WT{0:02}'.format(i) for i in range(1, 23)])

    # WV** = Weather in the Vicinity where ** has one of the following values:
    #        01 = Fog, ice fog, or freezing fog (may include heavy fog)
    #        03 = Thunder
    #        07 = Ash, dust, sand, or other blowing obstruction
    #        18 = Snow or ice crystals
    #        20 = Rain or snow shower
    codes.extend(['WV{0:02}'.format(i) for i in [1, 3, 7, 18, 20]])

    for code in codes:
        tmpdf = df.ix[df['code'] == code, :]
        if len(tmpdf) == 0:
            continue
        tmpdf.set_index(['year', 'month'], inplace=True)
        tmpdf = tmpdf.ix[:, list(range(2, 126, 4))].stack()
        tmpdf.index = (tmpdf.index.get_level_values(0).astype(str).values
                       + "-"
                       + tmpdf.index.get_level_values(1).astype(str).values
                       + "-"
                       + tmpdf.index.get_level_values(2).astype(str).values)

        # Get rid of bad dates, for example April 31.
        tmpdf.index = pd.to_datetime(tmpdf.index, errors='coerce')
        tmpdf = tmpdf[pd.notnull(tmpdf.index)]

        tmpdf = pd.DataFrame(tmpdf)
        tmpdf.columns = [code]
        tmpdf = tmpdf.ix[tsutils.parsedate(data.query_params['start_date'],
                                           strftime='%Y-%m-%d'):
                         tsutils.parsedate(data.query_params['end_date'],
                                           strftime='%Y-%m-%d'), :]
        try:
            ndf = ndf.join(tmpdf)
        except NameError:
            ndf = tmpdf

    ndf.index.name = 'Datetime'
    ndf.replace(to_replace=[-9999], value=[None], inplace=True)
    return ndf

if __name__ == '__main__':
    r = resource(
        r'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all',
        station='ASN00075020',
        start_date='2000-01-01',
        end_date='2001-01-01',
        )

    as_df = odo(r, pd.DataFrame)
    print('ghcnd')
    print(as_df)

    r = resource(
        r'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all',
        station='ASN00075020',
        start_date='10 years ago',
        end_date='9 years ago',
        )

    as_df = odo(r, pd.DataFrame)
    print('ghcnd')
    print(as_df)
