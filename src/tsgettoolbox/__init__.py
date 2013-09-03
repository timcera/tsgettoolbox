
import urllib
import urllib2
import re
import datetime

import baker
from voluptuous import required, any, all, length, range, Schema, coerce, Invalid
import ulmo
import pandas as pd

import tsutils

def valid_date(msg=None):
    '''
    This is a 'voluptuous' validation function.
    YYYY-MM-DD
    '''
    def f(v):
        try:
            year, month, day = re.findall(r'\d+', v)
            year, month, day = [int(i) for i in [year, month, day]]
            dt = datetime.datetime(year, month, day)
        except ValueError:
            raise Invalid(msg or ('date string {0} not valid'.format(v)))
    return f


def valid_period(msg=None):
    '''
    This is a 'voluptuous' validation function.
    It is a mess of a thing.  Tests for a valid ISO8601 period.
    '''
    def f(v):
        if v[0] != 'P':
            raise Invalid(msg or ('A valid ISO8601 period begins with "P", instead of {0}'.format(v)))
        if v[-1] == 'W':
            try:
                nweeks = float(v[1:-1])
                return v
            except ValueError:
                raise Invalid(msg or ('There should be a single number between the "P" and "W", instead have "{0}"'.format(v[1:-1])))

        allletters = re.findall(r'\a+', v)
        badletters = re.findall(r'[^PYMDTHMS]', ''.join(allletters))
        if badletters:
            raise Invalid(msg or ('A ISO8601 period can only contain the letters "PYMDTHMS" (or "P[n]W") instead of "{0}" in "{1}"'.format(badletters, v)))

        numbers = re.findall(r'\d+\.*\d*', v)
        letters = re.findall(r'[YMDHMS]', v)
        if len(numbers) != len(letters):
            raise Invalid(msg or ('There should be a single number followed by one of "YMDHMS" to represent a ISO8601 period in {0}'.format(v)))

        if v[1] == 'T':
            badletters = re.findall(r'[^HMS]', v[2:])
            if badletters:
                raise Invalid(msg or ('A ISO8601 period that begins with "PT" can only contain the letters "HMS" instead of "{0}" in "{1}"'.format(badletters, v)))

        old = 0
        for lt in 'PYMDTHmS':
            if lt == 'm':
                new = v.rfind('M')
            else:
                new = v.find(lt)
            if old > new:
                raise Invalid(msg or ('Not every key needs to be represented in a ISO8601 period string, but the order must be PYMDTHMS in {0}'.format(v)))
            old = new

        if 'T' in v[1:]:
            for words, match in zip(v[1:].split('T'), [r'YMD', r'HMS']):
                numbers = re.findall(r'\d+', words)
                letters = re.findall(r'[{0}]'.format(match), words)

                if len(numbers) != len(letters):
                    raise Invalid(msg or ('There should be a single number followed by one of "Y", "M", "D" to represent a ISO8601 period in {0}'.format(words)))
                badletters = re.findall(r'[^{0}]'.format(match), words)
                if badletters:
                    raise Invalid(msg or ('A ISO8601 period that contains a "T" can only contain the letters "YMD" before the "T" instead of "{0}" in "{1}"'.format(badletters, v)))

                if len(numbers) != len(letters):
                    raise Invalid(msg or ('There should be a single number followed by one of {0} to represent a ISO8601 period in {1}'.format(match, words)))
    return f


@baker.command
def usgs_station_detail(sites=None, stateCd=None, huc=None, bBox=None,
        countyCd=None, startDT=None, endDT=None, siteStatus='all',
        siteType=None, hasDataTypeCd='all', modifiedSince=None,
        parameterCd='all', agencyCd=None, altMin=None, altMax=None,
        aquiferCd=None, locAquiferCd=None, drainAreaMin=None,
        drainAreaMax=None, wellDepthMin=None, wellDepthMax=None,
        holeDepthMin=None, holeDepthMax=None, siteOutput='basic',
        seriesCatalogOutput='false', outputDataTypeCd='all', printURL=False):
    print _usgs_station_detail(**vars())


def _usgs_validate(sites=None, stateCd=None, huc=None, bBox=None,
        countyCd=None, startDT=None, endDT=None, siteStatus='all',
        siteType=None, hasDataTypeCd='all', modifiedSince=None,
        parameterCd='all', agencyCd=None, altMin=None, altMax=None,
        aquiferCd=None, locAquiferCd=None, drainAreaMin=None,
        drainAreaMax=None, wellDepthMin=None, wellDepthMax=None,
        holeDepthMin=None, holeDepthMax=None, siteOutput=None,
        seriesCatalogOutput=None, outputDataTypeCd='all'):

    # Filter out all keywords that have None as their value.
    # Since using 'vars()' must be first even though before error checks.
    nvars = vars()
    filtervars = {}
    for key in nvars:
        if not (nvars[key] == None or nvars[key] == 'all'):
            filtervars[key] = nvars[key]

    cnt = 0
    for testunique in ['sites', 'stateCd', 'huc', 'bBox', 'countyCd']:
        if testunique in filtervars.keys():
            cnt = cnt + 1
    if cnt != 1:
        raise Invalid('Must have one and only one of "sites", "stateCd", "huc", "bBox", and "countyCd" keywords.')

    # Make these into lists to easily validate. Later join to strings to make
    # URL.
    mvalues = ['sites', 'bBox', 'huc', 'countyCd', 'parameterCd',
            'siteType', 'aquiferCd', 'locAquiferCd', 'hasDataTypeCd']
    for mvalkey in mvalues:
        if filtervars.has_key(mvalkey):
            filtervars[mvalkey] = filtervars[mvalkey].split(',')

    validation = Schema({
        'sites' : [all(length(min=8, max=15), coerce(int))],
        'stateCd' : all(str, length(min=2, max=2)),
        'huc' : [any(all(length(min=2, max=2), coerce(int)), all(length(min=8,
            max=8), coerce(int)))],
        # Can't separately test range for lat and long...hmmm
        'bBox' : all(length(min=4,max=4), [all(any(coerce(int), coerce(float)),
            range(min=-180, max=180))]),
        'countyCd' : all(length(max=20), [all(length(min=5, max=5),
            coerce(int))]),
        'startDT' : valid_date(),
        'endDT' : valid_date(),
        'siteStatus' : any('all', 'active', 'inactive'),
        # Need to work on siteType
        'siteType' : [any('GW-MW','GW-TH','SB','SB-CV','SB-GWD','SB-TSM','SB-UZ','WE','LA','LA-EX','LA-OU','LA-SNK','LA-SH','LA-SR','FA','FA-CI','FA-CS','FA-DV','FA-FON','FA-GC','FA-HP','FA-QC','FA-LF','FA-OF','FA-PV','FA-SPS','FA-STS','FA-TEP','FA-WIW','FA-SEW','FA-WWD','FA-WWTP','FA-WDS','FA-WTP','FA-WU','AW','AG','AS')],
        'hasDataTypeCd' : [any('all', 'iv', 'uv', 'rt', 'dv', 'pk', 'sv',
            'gw', 'qw', 'id', 'aw', 'ad')],
        'modifiedSince' : valid_period(),
        'parameterCd' : [any('all', all(length(min=5, max=5), coerce(int)))],
        'agencyCd' : [all(length(max=5))],
        'altMin' : any(coerce(int), coerce(float)),
        'altMax' : any(coerce(int), coerce(float)),
        'aquiferCd' : [all(length(min=10,max=10))],
        'locAquiferCd' : [all(length(min=10,max=10))],
        'drainAreaMin' : any(coerce(int), coerce(float), range(min=0)),
        'drainAreaMax' : any(coerce(int), coerce(float), range(min=0)),
        'wellDepthMin' : any(coerce(int), coerce(float), range(min=0)),
        'wellDepthMax' : any(coerce(int), coerce(float), range(min=0)),
        'holeDepthMin' : any(coerce(int), coerce(float), range(min=0)),
        'holeDepthMax' : any(coerce(int), coerce(float), range(min=0)),
        'siteOutput': any('basic', 'expanded'),
        'seriesCatalogOutput': any('true', 'false'),
        'outputDataTypeCd': any('all', 'iv', 'uv', 'rt', 'dv', 'pk', 'sv', 'gw', 'id', 'aw', 'ad'),
        })

    validation(filtervars)

    for mvalkey in mvalues:
        if filtervars.has_key(mvalkey):
            filtervars[mvalkey] = ','.join(filtervars[mvalkey])
    return filtervars


def _usgs_station_detail(sites=None, stateCd=None, huc=None, bBox=None,
        countyCd=None, startDT=None, endDT=None, siteStatus='all',
        siteType=None, hasDataTypeCd='all', modifiedSince=None,
        parameterCd='all', agencyCd=None, altMin=None, altMax=None,
        aquiferCd=None, locAquiferCd=None, drainAreaMin=None,
        drainAreaMax=None, wellDepthMin=None, wellDepthMax=None,
        holeDepthMin=None, holeDepthMax=None, siteOutput='basic',
        seriesCatalogOutput='false', outputDataTypeCd='all', printURL=False):
    '''
    Local
    '''
    nvars = vars()
    del nvars['printURL']
    filtervars = _usgs_validate(**nvars)

    filtervars['format'] = 'rdb,1.0'

    baseurl = 'http://waterservices.usgs.gov/nwis/site/'
    datastr = urllib.urlencode(filtervars, True)
    if printURL:
        url = '{0}?{1}'.format(baseurl, urllib.urlencode(filtervars, True))
        return url
    else:
        fp = urllib2.urlopen(baseurl, datastr)
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
        for k,w in zip(keys, words):
            collect.setdefault(k, []).append(w)
    return collect



@baker.command
def get_por(*param_spec, **kwargs):
    '''
    Get station period of record.
    Use NWIS,02245500,00060,1440
    Use NWIS,02245500,00065,UNIT
    Use COOPS,8721100,WELEV,6
    Use COOPS,8721100,WELEV,60
    '''
    for spec in param_spec:
        orgabbr, station, param = spec.split(',')
        tsd = _get_por[orgabbr](station, param)


def _coops_get_data(station, param):
    pass

def _nwisdv_get_data(station, param):
    return _usgs_get_data(sites=station, parameterCd=param)

def _nwisuv_get_data(station, param):
    pass

def _ncdc_get_data(station, param):
    pass

_datadownload = {'COOPS': _coops_get_data,
                 'NWISDV': _nwisdv_get_data,
                 'NWISUV': _nwisuv_get_data,
                 'NCDC': _ncdc_get_data,
                 }


@baker.command(default=True)
def get_data(*param_specs, **kwds):
    try:
        start_date = kwds.pop('start_date')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except KeyError:
        start_date = None
    try:
        end_date = kwds.pop('start_date')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except KeyError:
        end_date = None
    if kwds:
        raise ValueError(
            '"start_date" and "end_date" are the only keywords allowed, you gave {0}'.format( kwds.keys()))

    for index in param_specs:
        orgabbr, station, param = index.split(',')
        if orgabbr[:4] == 'NWIS':
            if start_date:
                date_range = start_date
            if orgabbr == 'NWISDV':
                nts = ulmo.usgs.nwis.core.get_site_data(
                        station, service='daily',
                        date_range=date_range)
                param_interval = ':00003'
            if orgabbr == 'NWISIV':
                nts = ulmo.usgs.nwis.core.get_site_data(
                        station, service='instantaneous',
                        date_range=date_range)
                param_interval = ':00011'
            dates = [i['datetime'] for i in nts[param + param_interval]['values']]
            values = [float(i['value']) for i in nts[param + param_interval]['values']]
            nts = pd.DataFrame(pd.Series(values, index=dates),
                    columns=['{0}_{1}_{2}'.format(orgabbr, station, param)])
        if orgabbr == 'GHCN':
            nts = ulmo.ncdc.ghcn_daily.get_data(station, elements=param,
                    update=True, as_dataframe=True)
        if orgabbr == 'NCDC':
            nts = ulmo.ncdc.gsod.get_data(station, parameters=param,
                    start_date=start_date, end_date=end_date)
            dates = [i['datetime'] for i in nts[param + param_interval]['values']]
            values = [float(i['value']) for i in nts[param + param_interval]['values']]
            nts = pd.DataFrame(pd.Series(values, index=dates),
                    columns=['{0}_{1}_{2}'.format(orgabbr, station, param)])
        try:
            result = result.join(nts, how='outer')
        except NameError:
            result = nts
    tsutils.printiso(result)


@baker.command
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
    for site,param in [i.split(',') for i in param_spec]:
        rdbtab = _parse_rdb(_usgs_station_detail(sites=site,
        parameterCd=param, outputDataTypeCd=outputDataTypeCd))
        print rdbtab


def _usgs_get_data(sites=None, stateCd=None, huc=None, bBox=None,
        countyCd=None, startDT=None, endDT=None, siteStatus='all',
        siteType=None, hasDataTypeCd='all', modifiedSince=None,
        parameterCd='all', agencyCd=None, altMin=None, altMax=None,
        aquiferCd=None, locAquiferCd=None, drainAreaMin=None,
        drainAreaMax=None, wellDepthMin=None, wellDepthMax=None,
        holeDepthMin=None, holeDepthMax=None,
        printURL=False, dataType='dv'):

    nvars = vars()
    del nvars['printURL']
    del nvars['dataType']
    filtervars = _usgs_validate(**nvars)

    import json

    import dateutil.parser

    filtervars['format'] = 'json,1.1'

    baseurl = 'http://waterservices.usgs.gov/nwis/{0}/'.format(dataType)
    datastr = urllib.urlencode(filtervars, True)
    if printURL:
        url = '{0}?{1}'.format(baseurl, urllib.urlencode(filtervars, True))
        return url
    else:
        fp = urllib2.urlopen(baseurl, datastr)
        nts = json.loads(fp.read())
        data = []
        dateindex = []
        for item in nts['value']['timeSeries'][0]['values'][0]['value']:
            data.append(float(item['value']))
            dateindex.append(dateutil.parser.parse(item['dateTime']))
        return pd.DataFrame(pd.Series(data, index=dateindex,
            name='{0}_{1}'.format(sites, parameterCd)))


@baker.command
def usgs_daily(*param_spec, **kwargs):
    """
    Downloads hydrological data from the USGS site.

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
    begin_date : {None, str}, optional
        First date to be retrieved.  If None find the earliest date with an
        observation of all **param_spec.
    end_date : {None, str}, optional
        Last date to be retrieved.
        If None, uses the latest date with an observation of all **param_spec.

    Notes
    -----
    The list of data codes valid for the ``data_type`` parameters are available
    on the `USGS site <http://waterdata.usgs.gov/nwis/pmcodes/pmcodes?pm_group=All+--+include+all+parameter+groups&pm_search=&format=html_table&show=parameter_group_nm&show=parameter_nm>`_

    """

    import tsutils

    begin_date = kwargs.pop('begin_date', None)
    end_date = kwargs.pop('end_date', None)
    for index,site_param in enumerate(param_spec):
        site,param = site_param.split(',')
        nts = _usgs_get_data(sites=site, parameterCd=param,
                startDT=begin_date, endDT=end_date, dataType='dv')
        if index == 0:
            result = nts
        else:
            result = result.join(nts, how='outer')
    tsutils.printiso(result)


@baker.command
def usgs_unit(*param_spec, **kwargs):
    """
    Downloads unit (time interval as collected) hydrological data from the
    USGS site.

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
    on the `USGS site <http://waterdata.usgs.gov/nwis/pmcodes/pmcodes?pm_group=All+--+include+all+parameter+groups&pm_search=&format=html_table&show=parameter_group_nm&show=parameter_nm>`_

    """

    import tsutils

    begin_date = kwargs.pop('begin_date', None)
    end_date = kwargs.pop('end_date', None)
    for index, site_param in enumerate(param_spec):
        site, param = site_param.split(',')
        nts = _usgs_get_data(sites=site, parameterCd=param,
                startDT=begin_date, endDT=end_date, dataType='iv')
        if index == 0:
            result = nts
        else:
            result = result.join(nts, how='outer')
    tsutils.printiso(result)


def main():
    baker.run()

