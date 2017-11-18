"""
    This module provides access to data provided by the `United States Army
    Corps of Engineers`_ `Rivergages`_ web site.

    .. _United States Army Corps of Engineers: http://www.usace.army.mil/
    .. _Rivergages: http://rivergages.mvr.usace.army.mil/WaterControl/new/layout.cfm
"""
from ulmo.usace.rivergages.core import get_station_data
import pandas as pd

# def get_station_data(station_code, parameter, start=None, end=None,
#         min_value=None, max_value=None):


def ulmo_df(station_code,
            parameter,
            start_date=None,
            end_date=None):
    return get_station_data(station_code,
                            parameter,
                            start=pd.to_datetime(start_date),
                            end=pd.to_datetime(end_date))


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
