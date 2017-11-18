"""
    ulmo.usgs.eddn.core
    ~~~~~~~~~~~~~~~~~~~~~

    This module provides access to data provided by the `United States
    Geological Survey`_ `Emergency Data Distribution Network`_ web site.

    The `DCP message format`_ includes some header information that is parsed
    and the message body, with a variable number of characters. The format of
    the message body varies widely depending on the manufacturer of the
    transmitter, data logger, sensors, and the technician who programmed the
    DCP. The body can be simple ASCII, sometime with parameter codes and
    time-stamps embedded, sometimes not. The body can also be in
    'Pseudo-Binary' which is character encoding of binary data that uses 6 bits
    of every byte and guarantees that all characters are printable.


    .. _United States Geological Survey: http://www.usgs.gov/
    .. _Emergency Data Distribution Network: http://eddn.usgs.gov/
    .. _http://eddn.usgs.gov/dcpformat.html

"""
from ulmo.usgs.eddn import get_data, decode

# def get_data(
#         dcp_address, start=None, end=None, networklist='', channel='', spacecraft='Any', baud='Any',
#         electronic_mail='', dcp_bul='', glob_bul='', timing='', retransmitted='Y', daps_status='N',
#         use_cache=False, cache_path=None, as_dataframe=True):


def ulmo_df(dcp_address,
            parser,
            start_date=None,
            end_date=None):
    first = get_data(dcp_address,
                     start=start_date,
                     end=end_date)
    return decode(first,
                  parser).sort_index()


if __name__ == '__main__':
    r = ulmo_df('C5149430',
                'twdb_sutron',
                start_date='P5D',
                end_date='P1D')

    print('FL EVERYTHING')
    print(r)
