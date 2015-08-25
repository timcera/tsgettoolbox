
import datetime
from collections import defaultdict

from odo import odo, resource, convert
import pandas as pd
import requests


# NOAA/NOS Tides and Currents
# pd.read_csv('http://tidesandcurrents.noaa.gov/api/datagetter?
# begin_date=20130101&
# end_date=20130101&
# station=8454000&
# product=water_level&
# datum=mllw&
# units=metric&
# time_zone=gmt&
# application=web_services&
# format=csv',
#  index_col=0)

class NOS(object):
    def __init__(self, url, **query_params):
        params = {}
        params['interval'] = 'h'
        params['units'] = 'metric'
        params['time_zone'] = 'gmt'
        params['datum'] = 'mllw'
        params.update(query_params)

        params['format'] = 'csv'
        params['application'] = 'tsgettoolbox'
        self.url = url
        self.query_params = params

# Function to make `resource` know about the new NOS type.
@resource.register(r'http(s)?://tidesandcurrents\.noaa\.gov.*', priority=17)
def resource_nos(uri, **kwargs):
    return NOS(uri, **kwargs)

# Function to convert from NOS type to pd.DataFrame
@convert.register(pd.DataFrame, NOS)
def nos_to_df(data, **kwargs):
    settings_map = defaultdict(lambda: [{'metric':'', 'english':''}])
    settings_map['water_level'] = [
        {'metric':'m', 'english':'ft'}, 'h']  # Preliminary or verified water levels, depending on availability.
    settings_map['air_temperature'] = [
        {'metric':'deg_C', 'english':'deg_F'}, 'h']  # Air temperature as measured at the station.
    settings_map['water_temperature'] = [
        {'metric':'deg_C', 'english':'deg_F'}, 'h']  # Water temperature as measured at the station.
    settings_map['wind'] = [
        {'metric':'m/s', 'english':'ft/s'}, 'h']  # Wind speed, direction, and gusts as measured at the station.
    settings_map['air_pressure'] = [
        {'metric':'mb', 'english':'mb'}, 'h']  # Barometric pressure as measured at the station.
    settings_map['air_gap'] = [
        {'metric':'m', 'english':'ft'}, 'h']  # Air Gap (distance between a bridge and the water's surface) at the station.
    settings_map['conductivity'] = [
        {'metric':'mS/cm', 'english':'mS/cm'}, 'h']  # The water's conductivity as measured at the station.
    settings_map['visibility'] = [
        {'metric':'km', 'english':'nm'}, 'h']  # Visibility from the station's visibility sensor. A measure of atmospheric clarity.
    settings_map['humidity'] = [
        {'metric':'percent', 'english':'percent'}, 'h']  # Relative humidity as measured at the station.
    settings_map['salinity'] = [
        {'metric':'PSU', 'english':'PSU'}, 'h']  # Salinity and specific gravity data for the station.
    settings_map['hourly_height'] = [
        {'metric':'m', 'english':'ft'}, 'h']  # Verified hourly height water level data for the station.
    settings_map['high_low'] = [
        {'metric':'m', 'english':'ft'}, None]  # Verified high/low water level data for the station.
    settings_map['daily_mean'] = [
        {'metric':'m', 'english':'ft'}, None]  # Verified daily mean water level data for the station.
    settings_map['monthly_mean'] = [
        {'metric':'m', 'english':'ft'}, None]  # Verified monthly mean water level data for the station.
    settings_map['one_minute_water_level'] = [
        {'metric':'m', 'english':'ft'}, None]  # One minute water level data for the station.
    settings_map['predictions'] = [
        {'metric':'m', 'english':'ft'}, 'h']  # 6 minute predictions water level data for the station.
    settings_map['datums'] = [
        {'metric':'m', 'english':'ft'}, None]  # datums data for the stations.
    settings_map['currents'] = [
        {'metric':'m/s', 'english':'ft/s'}, 'h']  # Currents data for currents stations.
    df = pd.read_csv(
                     requests.Request(
                         'GET',
                         data.url,
                         params=data.query_params,
                     ).prepare().url,
                     index_col=0,
                     parse_dates=True)
    new_column_names = []
    for icolumn_name in df.columns:
        ncolumn_name = icolumn_name.lower().strip().replace(' ', '_')
        units = settings_map[ncolumn_name][0][data.query_params['units']]
        new_column_names.append(('NOS',
                                 data.query_params['station'],
                                 ncolumn_name,
                                 units))
    df.columns = ['-'.join(i).rstrip('-') for i in new_column_names]
    df.index.name = 'Datetime-{0}'.format(data.query_params['time_zone'].upper())
    return df

if __name__ == '__main__':
    r = resource(
        r'http://tidesandcurrents.noaa.gov/api/datagetter',
        begin_date='20020101',
        end_date='20020102',
        range=1,
        station='8720218',
        product='water_level',
        )

    as_df = odo(r, pd.DataFrame)
    print('tidesandcurrents')
    print(as_df)
