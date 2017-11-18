"""
    ulmo.lcra.hydromet.core
    ~~~~~~~~~~~~~~~~~~~~~~~
    This module provides access to hydrologic and climate data in the Colorado
    River Basin (Texas) provided by the `Lower Colorado River Authority`_
    `Hydromet`_ web site and web service.
    .. _Lower Colorado River Authority: http://www.lcra.org
    .. _Hydromet: http://hydromet.lcra.org
"""
from ulmo.lcra.hydromet.core import get_site_data, get_current_data
import pandas as pd


def ulmo_df(site_code,
            parameter_code,
            start_date=None,
            end_date=None,
            dam_site_location='head'):
    if parameter_code.lower() in ['upperbasin', 'lowerbasin']:
        # def get_current_data(service, as_geojson=False):
        df = pd.DataFrame(get_current_data('get' + parameter_code))
        return df.set_index('location')

    # def get_site_data(site_code, parameter_code, as_dataframe=True,
    #                  start_date=None, end_date=None, dam_site_location='head'):
    return get_site_data(str(site_code),
                         parameter_code,
                         start_date=pd.to_datetime(start_date),
                         end_date=pd.to_datetime(end_date),
                         dam_site_location=dam_site_location)


if __name__ == '__main__':
    #    import time
    #
    #    r = ulmo_df('blah',
    #                'upperbasin')
    #
    #    print('UB EVERYTHING')
    #    print(r)
    #
    #    time.sleep(20)

    r = ulmo_df(4598,
                'stage',
                start_date='2015-11-04',
                end_date='2015-12-05')

    print('UB EVERYTHING')
    print(r)
