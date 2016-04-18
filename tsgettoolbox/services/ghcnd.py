

from odo import odo, resource, convert
import pandas as pd


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
    df = pd.read_fwf(data.url+'/'+data.query_params['station']+'.dly',
                     widths=[11, 4, 2, 4]+[5, 1, 1, 1]*31)
    df.columns = ['station', 'year', 'month', 'code'] + [
        '{0}{1}'.format(col, day)
        for day in range(1, 32)
        for col in ['', 'm', 'q', 's']]
    codes = [(0.1, 'TMAX'), (0.1, 'TMIN'), (0.1, 'PRCP'), (1.0, 'SNOW'),
             (1.0, 'SNWD')]
    for multiplier, code in codes:
        tmpdf = df.ix[df['code'] == code, :]
        if len(tmpdf) == 0:
            continue
        tmpdf = tmpdf.set_index(['year', 'month'])
        tmpdf = tmpdf.ix[:, range(2, 126, 4)].stack()
        tmpdf.index = (tmpdf.index.get_level_values(0).astype(str).values
                       + "-"
                       + tmpdf.index.get_level_values(1).astype(str).values
                       + "-"
                       + tmpdf.index.get_level_values(2).astype(str).values)
        tmpdf.index = pd.to_datetime(tmpdf.index, errors='coerce')
        tmpdf = tmpdf[pd.notnull(tmpdf.index)]
        tmpdf = pd.DataFrame(tmpdf)
        tmpdf.columns = [code]
        tmpdf = tmpdf.ix[data.query_params['start_date']:
                         data.query_params['end_date'], :]
        tmpdf[code] = tmpdf[code].astype(float)*multiplier
        try:
            ndf = ndf.join(tmpdf)
        except NameError:
            ndf = tmpdf

    ndf.index.name = 'Datetime'
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

