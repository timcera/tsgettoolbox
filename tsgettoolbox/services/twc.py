"""
Direct access to KBDI from `Texas Weather Connection`_.

Access the Texas `Daily Keetch-Byram Drought Index (KBDI)`_ dataset.

.. _Texas Weather Connection: http://twc.tamu.edu/
.. _Daily Keetch-Byram Drought Index (KBDI): http://twc.tamu.edu/drought/kbdi
"""
from __future__ import print_function

import pandas as pd

from tsgettoolbox.ulmo.twc.kbdi.core import get_data


def ulmo_df(county=None, start_date=None, end_date=None):

    return get_data(
        county=county,
        start=pd.to_datetime(start_date),
        end=pd.to_datetime(end_date),
        as_dataframe=True,
    )


if __name__ == "__main__":
    #    import time
    #
    #    r = ulmo_df('blah',
    #                'upperbasin')
    #
    #    print('UB EVERYTHING')
    #    print(r)
    #
    #    time.sleep(20)

    r = ulmo_df(48001, start_date="2015-11-04", end_date="2015-12-05")

    print("UB EVERYTHING")
    print(r)
