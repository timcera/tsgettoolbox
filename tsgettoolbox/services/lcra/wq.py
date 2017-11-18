"""
    ulmo.lcra.waterquality.core
    ~~~~~~~~~~~~~~~~~~~~~
    This module provides access to data provided by the `Lower Colorado
    River Authority`_ `Water Quality`_ web site.
    .. _Lower Colorado River Authority: http://www.lcra.org
    .. _Water Quality: http://waterquality.lcra.org/
"""
from ulmo.lcra.waterquality.core import get_historical_data, get_recent_data

# def get_historical_data(site_code, start=None, end=None, as_dataframe=False):
# def get_recent_data(site_code, as_dataframe=False):


def ulmo_df(site_code,
            start_date=None,
            end_date=None,
            historical=True):
    if historical is True:
        return get_historical_data(site_code,
                                   start=start_date,
                                   end=end_date,
                                   as_dataframe=True)
    return get_recent_data(site_code,
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

    r = ulmo_df(6977,
                historical=False,
                start_date='2015-11-04',
                end_date='2015-12-05')

    print('UB EVERYTHING')
    print(r)
