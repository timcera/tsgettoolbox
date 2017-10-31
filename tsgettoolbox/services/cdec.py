
from ulmo import cdec
import pandas as pd


def ulmo_df(station_id,
            sensor_num=None,
            dur_code=None,
            start_date=None,
            end_date=None):

    if isinstance(sensor_num, (str, bytes)):
        sensor_num = [int(i) for i in sensor_num.split('.')]
    elif isinstance(sensor_num, int):
        sensor_num = [sensor_num]

    if isinstance(dur_code, (str, bytes)):
        dur_code = dur_code.split(',')

        mapd = {'D': 'daily',
                'E': 'event',
                'H': 'hourly',
                'M': 'monthly'}

        dur_code = [mapd[i] for i in dur_code]

    d = cdec.historical.get_data([station_id],
                                 sensor_ids=sensor_num,
                                 resolutions=dur_code,
                                 start=start_date,
                                 end=end_date)

    nd = pd.DataFrame()
    for key in d[station_id]:
        nnd = pd.DataFrame(d[station_id][key])
        nnd.columns = [key]
        nd = nd.join(nnd, how='outer')
    return nd


if __name__ == '__main__':
    """
    """

    r = ulmo_df('PAR',
                start_date='2017-01-01',
                end_date='2017-10-02',
                dur_code='D',
                sensor_num=45)

    print('PAR PRECIPITATION')
    print(r)

    r = ulmo_df('PAR',
                start_date='2017-01-01',
                end_date='2017-10-02',
                dur_code='H',
                sensor_num=6)

    print('PAR RESERVOIR VOLUME')
    print(r)

    r = ulmo_df('PAR',
                start_date='2017-01-01',
                end_date='2017-10-02',
                dur_code='H')

    print('PAR HOURLY')
    print(r)

    r = ulmo_df('PAR',
                start_date='2017-01-01',
                end_date='2017-10-02')

    print('PAR EVERYTHING')
    print(r)
