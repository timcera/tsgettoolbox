# -*- coding: utf-8 -*-
"""
Access data provided by the `United States Army Corps of Engineers`_.

Access data from the USACE `Tulsa District Water Control`_ web site.

.. _United States Army Corps of Engineers: http://www.usace.army.mil/
.. _Tulsa District Water Control: http://www.swt-wc.usace.army.mil/

"""
import datetime

import pandas as pd

from tsgettoolbox.ulmo.usace.swtwc.core import get_station_data

# def get_station_data(station_code, date=None, as_dataframe=False):


def ulmo_df(station_code, date=None):
    if date is None:
        date = datetime.datetime.now()
    else:
        date = pd.to_datetime(date)
    alldict = get_station_data(station_code, date=date, as_dataframe=True)
    df = alldict["values"]
    df.columns = [
        "{}:{}".format(i, alldict["variables"][i]["unit"]) for i in df.columns
    ]
    df.columns = [i.replace("  ", "_").replace(" ", "_") for i in df.columns]
    df = df.tz_localize(alldict["timezone"])
    return df


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

    r = ulmo_df("PTTK1", date="2017-11-30")

    print("PTTK1 EVERYTHING")
    print(r)
