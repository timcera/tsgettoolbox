"""
swtwc               US/region station:USACE Southwest Division, Tulsa
                    Water Control
"""
import datetime

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox.ulmo.usace.swtwc.core import get_station_data

__all__ = ["swtwc"]

# def get_station_data(station_code, date=None, as_dataframe=False):


@cltoolbox.command("swtwc", formatter_class=HelpFormatter)
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


@tsutils.copy_doc(swtwc_cli)
def swtwc(station_code, date=None):
    """US/region station:USACE Southwest Division, Tulsa Water Control"""
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
