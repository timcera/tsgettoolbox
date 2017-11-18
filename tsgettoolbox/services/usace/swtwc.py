"""
    This module provides access to data provided by the `United States Army
    Corps of Engineers`_ `Tulsa District Water Control`_ web site.

    .. _United States Army Corps of Engineers: http://www.usace.army.mil/
    .. _Tulsa District Water Control: http://www.swt-wc.usace.army.mil/

"""
from ulmo.usace.swtwc.core import get_station_data
import pandas as pd

# def get_station_data(station_code, date=None, as_dataframe=False):


def ulmo_df(station_code,
            date=None):
    return get_station_data(station_code,
                            date=date,
                            as_dataframe=True)


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
