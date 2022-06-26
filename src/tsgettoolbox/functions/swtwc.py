# -*- coding: utf-8 -*-
"""
Access data provided by the `United States Army Corps of Engineers`_.

Access data from the USACE `Tulsa District Water Control`_ web site.

.. _United States Army Corps of Engineers: http://www.usace.army.mil/
.. _Tulsa District Water Control: http://www.swt-wc.usace.army.mil/

https://www.swt-wc.usace.army.mil/webdata/gagedata/EUFO2.current.html
https://www.swt-wc.usace.army.mil/webdata/gagedata/PTTK1.20211231.html
"""
import datetime

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

from tsgettoolbox.ulmo.usace.swtwc.core import get_station_data

__all__ = ["swtwc"]

# def get_station_data(station_code, date=None, as_dataframe=False):


@mando.command("swtwc", formatter_class=HelpFormatter, doctype="numpy")
def swtwc_cli(station_code, date=None):
    """US/region station:USACE Southwest Division, Tulsa Water Control

    Parameters
    ----------
    station_code
        The station code.
    date
        The date for the downloaded data.
    """
    tsutils.printiso(swtwc(station_code, date=date))


def swtwc(station_code, date=None):
    date = datetime.datetime.now() if date is None else pd.to_datetime(date)
    alldict = get_station_data(station_code, date=date, as_dataframe=True)
    df = alldict["values"]
    df.columns = [f"{i}:{alldict['variables'][i]['unit']}" for i in df.columns]
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

    r = swtwc("PTTK1", date="2021-11-30")

    print("PTTK1 EVERYTHING")
    print(r)
