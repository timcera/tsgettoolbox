
import six.moves.urllib.parse as urllib_parse
import six.moves.urllib.request as urllib_request

import re
import datetime

import baker
from voluptuous import Any, All, Length, Range, Schema, Coerce, Invalid
import pandas as pd

from tstoolbox import tsutils


def valid_date(msg=None):
    '''
    This is a 'voluptuous' validation function.
    YYYY-MM-DD
    '''
    def f(v):
        try:
            dt = pd.datetools.parse(v)
        except TypeError:
            raise Invalid(msg or ('date string {0} not valid'.format(v)))
    return f


def valid_period(msg=None):
    '''
    This is a 'voluptuous' validation function.
    It is a mess of a thing.  Tests for a valid ISO8601 period.
    '''
    def f(v):
        if v[0] != 'P':
            raise Invalid(msg or ('''
*
*   A valid ISO8601 period begins with "P", instead of
*   {0}.
*
'''.format(v)))
        if v[-1] == 'W':
            try:
                nweeks = float(v[1:-1])
                return v
            except ValueError:
                raise Invalid(msg or ('''
*
*   There should be a single number between the "P" and "W", instead have
*   "{0}"
*
'''.format(v[1:-1])))

        allletters = re.findall(r'\a+', v)
        badletters = re.findall(r'[^PYMDTHMS]', ''.join(allletters))
        if badletters:
            raise Invalid(msg or ('''
*
*   A ISO8601 period can only contain the letters "PYMDTHMS" (or "P[n]W")
*   instead of "{0}" in "{1}"
*
'''.format(badletters, v)))

        numbers = re.findall(r'\d+\.*\d*', v)
        letters = re.findall(r'[YMDHMS]', v)
        if len(numbers) != len(letters):
            raise Invalid(msg or ('''
*
*   There should be a single number followed by one of "YMDHMS" to represent
*   an ISO8601 period in {0}.
*
'''.format(v)))

        if v[1] == 'T':
            badletters = re.findall(r'[^HMS]', v[2:])
            if badletters:
                raise Invalid(msg or ('''
*
*   A ISO8601 period that begins with "PT" can only contain the letters
*   "HMS" instead of "{0}" in "{1}"
*
'''.format(badletters, v)))

        old = 0
        for lt in 'PYMDTHmS':
            if lt == 'm':
                new = v.rfind('M')
            else:
                new = v.find(lt)
            if old > new:
                raise Invalid(msg or ('''
*
*   Not every key needs to be represented in a ISO8601 period string, but
*   the order must be PYMDTHMS in {0}
*
'''.format(v)))
            old = new

        if 'T' in v[1:]:
            for words, match in zip(v[1:].split('T'), [r'YMD', r'HMS']):
                numbers = re.findall(r'\d+', words)
                letters = re.findall(r'[{0}]'.format(match), words)

                if len(numbers) != len(letters):
                    raise Invalid(msg or ('''
*
*   There should be a single number followed by one of "Y", "M", "D" to
*   represent a ISO8601 period in {0}.
*
'''.format(words)))

                badletters = re.findall(r'[^{0}]'.format(match), words)
                if badletters:
                    raise Invalid(msg or ('''
*
*   A ISO8601 period that contains a "T" can only contain the letters "YMD"
*   before the "T" instead of "{0}" in "{1}".
*
'''.format(badletters, v)))

                if len(numbers) != len(letters):
                    raise Invalid(msg or ('''
*
*   There should be a single number followed by one of {0} to represent a
*   ISO8601 period in {1}.
*
'''.format(match, words)))

    return f



def usgs_station_detail(sites=None, stateCd=None, huc=None, bBox=None,
                        countyCd=None, startDT=None, endDT=None,
                        siteStatus='all', siteType=None,
                        hasDataTypeCd='all', modifiedSince=None,
                        parameterCd='all', agencyCd=None, altMin=None,
                        altMax=None, aquiferCd=None, locAquiferCd=None,
                        drainAreaMin=None, drainAreaMax=None,
                        wellDepthMin=None, wellDepthMax=None,
                        holeDepthMin=None, holeDepthMax=None,
                        siteOutput='basic', seriesCatalogOutput='false',
                        outputDataTypeCd='all', printURL=False):
    print(_usgs_station_detail(**vars()))


def _usgs_validate(sites=None, stateCd=None, huc=None, bBox=None,
                   countyCd=None, startDT=None, endDT=None,
                   siteStatus='all', siteType=None, hasDataTypeCd='all',
                   modifiedSince=None, parameterCd='all', agencyCd=None,
                   altMin=None, altMax=None, aquiferCd=None,
                   locAquiferCd=None, drainAreaMin=None, drainAreaMax=None,
                   wellDepthMin=None, wellDepthMax=None, holeDepthMin=None,
                   holeDepthMax=None, siteOutput=None,
                   seriesCatalogOutput=None, outputDataTypeCd='all'):

    # Filter out all keywords that have None as their value.
    # Since using 'vars()' must be first even though before error checks.
    nvars = vars()
    filtervars = {}
    for key in nvars:
        if (nvars[key] is not None or nvars[key] == 'all'):
            filtervars[key] = nvars[key]

    cnt = 0
    for testunique in ['sites', 'stateCd', 'huc', 'bBox', 'countyCd']:
        if testunique in list(filtervars.keys()):
            cnt = cnt + 1
    if cnt != 1:
        raise Invalid('''
*
*   Must have one and only one of "sites", "stateCd", "huc", "bBox", and
*   "countyCd" keywords.
*
''')

    # Make these into lists to easily validate. Later join to strings to make
    # URL.
    mvalues = ['sites', 'bBox', 'huc', 'countyCd', 'parameterCd',
               'siteType', 'aquiferCd', 'locAquiferCd', 'hasDataTypeCd']
    for mvalkey in mvalues:
        if mvalkey in filtervars:
            filtervars[mvalkey] = filtervars[mvalkey].split(',')

    validation = Schema({
        'sites': [All(Length(min=8, max=15), Coerce(int))],
        'stateCd': All(str, Length(min=2, max=2)),
        'huc': [Any(All(Length(min=2, max=2), Coerce(int)), All(Length(min=8,
                max=8), Coerce(int)))],
        # Can't separately test range for lat and long...hmmm
        'bBox': All(Length(min=4, max=4), [All(Any(Coerce(int), Coerce(float)),
                    Range(min=-180, max=180))]),
        'countyCd': All(Length(max=20), [All(Length(min=5, max=5),
                        Coerce(int))]),
        'startDT': valid_date(),
        'endDT': valid_date(),
        'siteStatus': Any('all', 'active', 'inactive'),
        # Need to work on siteType
        'siteType': [Any('GW-MW', 'GW-TH', 'SB', 'SB-CV', 'SB-GWD',
                     'SB-TSM', 'SB-UZ', 'WE', 'LA', 'LA-EX', 'LA-OU',
                     'LA-SNK', 'LA-SH', 'LA-SR', 'FA', 'FA-CI', 'FA-CS',
                     'FA-DV', 'FA-FON', 'FA-GC', 'FA-HP', 'FA-QC', 'FA-LF',
                     'FA-OF', 'FA-PV', 'FA-SPS', 'FA-STS', 'FA-TEP',
                     'FA-WIW', 'FA-SEW', 'FA-WWD', 'FA-WWTP', 'FA-WDS',
                     'FA-WTP', 'FA-WU', 'AW', 'AG', 'AS')],
        'hasDataTypeCd': [Any('all', 'iv', 'uv', 'rt', 'dv', 'pk', 'sv',
                          'gw', 'qw', 'id', 'aw', 'ad')],
        'modifiedSince': valid_period(),
        'parameterCd': [Any('all', All(Length(min=5, max=5), Coerce(int)))],
        'agencyCd': [All(Length(max=5))],
        'altMin': Any(Coerce(int), Coerce(float)),
        'altMax': Any(Coerce(int), Coerce(float)),
        'aquiferCd': [All(Length(min=10, max=10))],
        'locAquiferCd': [All(Length(min=10, max=10))],
        'drainAreaMin': Any(Coerce(int), Coerce(float), Range(min=0)),
        'drainAreaMax': Any(Coerce(int), Coerce(float), Range(min=0)),
        'wellDepthMin': Any(Coerce(int), Coerce(float), Range(min=0)),
        'wellDepthMax': Any(Coerce(int), Coerce(float), Range(min=0)),
        'holeDepthMin': Any(Coerce(int), Coerce(float), Range(min=0)),
        'holeDepthMax': Any(Coerce(int), Coerce(float), Range(min=0)),
        'siteOutput': Any('basic', 'expanded'),
        'seriesCatalogOutput': Any('true', 'false'),
        'outputDataTypeCd': Any('all', 'iv', 'uv', 'rt', 'dv', 'pk', 'sv',
                                'gw', 'id', 'aw', 'ad'),
        })

    validation(filtervars)

    for mvalkey in mvalues:
        if mvalkey in filtervars:
            filtervars[mvalkey] = ','.join(filtervars[mvalkey])
    return filtervars


def _usgs_station_detail(sites=None, stateCd=None, huc=None, bBox=None,
                         countyCd=None, startDT=None, endDT=None,
                         siteStatus='all', siteType=None,
                         hasDataTypeCd='all', modifiedSince=None,
                         parameterCd='all', agencyCd=None, altMin=None,
                         altMax=None, aquiferCd=None, locAquiferCd=None,
                         drainAreaMin=None, drainAreaMax=None,
                         wellDepthMin=None, wellDepthMax=None,
                         holeDepthMin=None, holeDepthMax=None,
                         siteOutput='basic', seriesCatalogOutput='false',
                         outputDataTypeCd='all', printURL=False):
    '''
    Local
    '''
    nvars = vars()
    del nvars['printURL']
    filtervars = _usgs_validate(**nvars)

    filtervars['format'] = 'rdb,1.0'

    baseurl = 'http://waterservices.usgs.gov/nwis/site/'
    datastr = urllib_parse.urlencode(filtervars, True)
    if printURL:
        url = '{0}?{1}'.format(baseurl,
                               urllib_parse.urlencode(filtervars, True))
        return url
    else:
        fp = urllib_request.urlopen(baseurl, datastr)
        return fp.read()


def _parse_rdb(table):
    table = table.split('\n')
    cnt_non_comment = 0
    collect = {}
    for line in table:
        if not line:
            continue
        if line[0] == '#':
            continue
        words = line.split('\t')
        cnt_non_comment = cnt_non_comment + 1
        if cnt_non_comment == 1:
            keys = words
            continue
        if cnt_non_comment == 2:
            continue
        for k, w in zip(keys, words):
            collect.setdefault(k, []).append(w)
    return collect


def _nos(station,
         parameter,
         begin_date=None,
         end_date=None,
         datum='NAVD',
         units='metric',
         time_zone='lst'):
    filtervars = {}
    filtervars['station'] = station
    filtervars['datum'] = datum
    filtervars['metric'] = metric
    filtervars['time_zone'] = time_zone
    filtervars['format'] = 'json'
    filtervars['application'] = 'tsgettoolbox'

    if begin_date is not None:
        filtervars['begin_date'] = begin_date
    if end_date is not None:
        filtervars['end_date'] = end_date

    baseurl = 'http://tidesandcurrents.noaa.gov/api/datagetter/'
    url = '{0}?{1}'.format(baseurl,
                           urllib_parse.urlencode(filtervars, True))
    if printURL:
        return url
    else:
        nts = pd.io.json.read_json(url)
        data = []
        dateindex = []
        for item in nts['data']:
            data.append(float(item['v']))
            dateindex.append(pd.datetools.parse(item['t']))
        return pd.DataFrame(pd.Series(data, index=dateindex,
                            name='{0}_{1}_{2}'.format(sites,
                                                      dataType, parameterCd)))


@baker.command
def get_station_list():
    pass


@baker.command
def get_station_metadata():
    pass


@baker.command
def get_data(*param_specs, **kwds):
    try:
        start_date = kwds.pop('start_date')
    except KeyError:
        start_date = None
    try:
        end_date = kwds.pop('end_date')
    except KeyError:
        end_date = None
    if kwds:
        raise ValueError('''
*
*   "start_date" and "end_date" are the only keywords allowed, you gave
*   {0}
*
'''.format(list(kwds.keys())))

    for index in param_specs:
        orgabbr, station, param = index.split(',')
        if orgabbr.lower()[:4] == 'nwis':
            if orgabbr.lower() == 'nwisdv':
                nts = _nwis_daily('{0},{1}'.format(station, param),
                        start_date=start_date, end_date=end_date)
            elif orgabbr.lower() == 'nwisiv':
                nts = _nwis_instant('{0},{1}'.format(station, param),
                        start_date=start_date, end_date=end_date)
        if orgabbr.lower() == 'ghcn':
            nts = ulmo.ncdc.ghcn_daily.get_data(
                station, elements=param, update=True, as_dataframe=True)
        if orgabbr.lower() == 'ncdc':
            nts = ulmo.ncdc.gsod.get_data(station, parameters=param,
                  start_date=start_date, end_date=end_date)
            dates = [i['datetime']
                     for i in nts[param + param_interval]['values']]
            values = [float(i['value'])
                      for i in nts[param + param_interval]['values']]
            nts = pd.DataFrame(pd.Series(values, index=dates),
                  columns=['{0}_{1}_{2}'.format(orgabbr, station, param)])
        if orgabbr.lower() == 'nos':
            nts = _nos(station, parameters=param, start_date=start_date,
                    end_data=end_date)
        try:
            result = result.join(nts, how='outer')
        except NameError:
            result = nts
    return tsutils.printiso(result)


def usgs_get_por(*param_spec, **kwargs):
    '''
    Get USGS station/parameter period of record.
    :param param_spec: A string with no spaces identifying the
        station_id,parameter_code of the desired data.  For example:
        '02245500,00060' This format allows for many parameters or stations to
        be requested at the same time.  If the parameter_code is left blank or
        '*' in single quotes, then all parameters for that station are
        downloaded.  You cannot leave the station_id blank.
        station_id : 2- to 15-digit identification number of the site whose
            information must be downloaded.
        parameter_code : String made up of 5 digits representing the
            parameter.  To list the parameters collected at a station use
            'tsgettoolbox usgs_station_detail'
    '''
    outputDataTypeCd = kwargs.pop('outputDataTypeCd', 'dv')
    for site, param in [i.split(',') for i in param_spec]:
        rdbtab = _parse_rdb(_usgs_station_detail(sites=site,
                            parameterCd=param,
                            outputDataTypeCd=outputDataTypeCd))
        print(rdbtab)


def _usgs_get_data(sites=None, stateCd=None, huc=None, bBox=None,
                   countyCd=None, startDT=None, endDT=None,
                   siteStatus='all', siteType=None, hasDataTypeCd='all',
                   modifiedSince=None, parameterCd='all', agencyCd=None,
                   altMin=None, altMax=None, aquiferCd=None,
                   locAquiferCd=None, drainAreaMin=None, drainAreaMax=None,
                   wellDepthMin=None, wellDepthMax=None, holeDepthMin=None,
                   holeDepthMax=None, printURL=False, dataType='dv'):

    nvars = vars()

    del nvars['dataType']
    del nvars['printURL']

    import dateutil.parser

    filtervars = _usgs_validate(**nvars)

    filtervars['format'] = 'json,1.1'

    # Want to have all the USGS/NWIS data AND station functions use the same
    # keyword arguements.  Then just delete the unused ones for the
    # particular function.
    del filtervars['hasDataTypeCd']
    del filtervars['outputDataTypeCd']

    baseurl = 'http://waterservices.usgs.gov/nwis/{0}/'.format(dataType)
    url = '{0}?{1}'.format(baseurl,
                           urllib_parse.urlencode(filtervars, True))
    if printURL:
        return url
    else:
        nts = pd.io.json.read_json(url)
        data = []
        dateindex = []
        for item in nts['value']['timeSeries'][0]['values'][0]['value']:
            data.append(float(item['value']))
            dateindex.append(dateutil.parser.parse(item['dateTime']))
        return pd.DataFrame(pd.Series(data, index=dateindex,
                            name='{0}_{1}_{2}'.format(sites,
                                                      dataType, parameterCd)))


def _nwis_daily(*param_spec, **kwargs):
    """
    Downloads daily hydrological data from the United State Geological
    Survey (USGS), National Water Information System site.

    Parameters
    ----------
    param_spec : str
        A string with no spaces identifying the station_id,parameter_code of
        the desired data.  For example: '02245500,00060'
        This format allows for many parameters or stations to be requested at
        the same time.  If the parameter_code is left blank or '*' in single
        quotes, then all parameters for that station are downloaded.  You
        cannot leave the station_id blank.
        station_id : str
            2- to 15-digit identification number of the site whose information
            must be downloaded.
        parameter_code : str
            String made up of 5 digits representing the parameter.  To list
            the parameters collected at a station use 'tsgettoolbox
            usgs_station_detail'
    start_date : {None, str}, optional
        First date to be retrieved.  If None find the earliest date with an
        observation of all **param_spec.
    end_date : {None, str}, optional
        Last date to be retrieved.
        If None, uses the latest date with an observation of all **param_spec.

    Notes
    -----
    The list of data codes valid for the ``data_type`` parameters are available
    on the `USGS site
    <http://waterdata.usgs.gov/nwis/pmcodes/pmcodes?pm_group=All+--+include+all+parameter+groups&pm_search=&format=html_table&show=parameter_group_nm&show=parameter_nm>`_

    """

    start_date = kwargs.pop('start_date', None)
    end_date = kwargs.pop('end_date', None)
    for index, site_param in enumerate(param_spec):
        site, param = site_param.split(',')
        nts = _usgs_get_data(sites=site, parameterCd=param,
                             startDT=start_date, endDT=end_date,
                             dataType='dv')
        if index == 0:
            result = nts
        else:
            result = result.join(nts, how='outer')
    return result


def _nwis_instant(*param_spec, **kwargs):
    """
    Downloads unit (time interval as collected) hydrological data from the
    United State Geological Survey (USGS), National Water Information System
    site.

    Parameters
    ----------
    :param param_spec: A string with no spaces identifying the
        station_id,parameter_code of the desired data.  For example:
        '02245500,00060' This format allows for many parameters or stations to
        be requested at the same time.  If the parameter_code is left blank or
        '*' in single quotes, then all parameters for that station are
        downloaded.  You cannot leave the station_id blank.
        station_id : 2- to 15-digit identification number of the site whose
            information must be downloaded.
        parameter_code : String made up of 5 digits representing the
            parameter.  To list the parameters collected at a station use
            'tsgettoolbox usgs_station_detail'
    :param begin_date: First date to be retrieved.  If None find the earliest
        date with an observation of all **param_spec.
    :param end_date: Last date to be retrieved.  If None, uses the latest date
        with an observation of all **param_spec.

    Notes
    -----
    The list of data codes valid for the ``data_type`` parameters are available
    on the `USGS site
    <http://waterdata.usgs.gov/nwis/pmcodes/pmcodes?pm_group=All+--+include+all+parameter+groups&pm_search=&format=html_table&show=parameter_group_nm&show=parameter_nm>`_

    """

    start_date = kwargs.pop('start_date', None)
    end_date = kwargs.pop('end_date', None)
    for index, site_param in enumerate(param_spec):
        site, param = site_param.split(',')
        nts = _usgs_get_data(sites=site, parameterCd=param,
                             startDT=start_date, endDT=end_date,
                             dataType='iv')
        if index == 0:
            result = nts
        else:
            result = result.join(nts, how='outer')
    return result


def main():
    baker.run()
