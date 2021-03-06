"""Download data from Florida Automated Weather Network (FAWN)."""

import datetime

import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

import mechanize

#  "referrer": "https://fawn.ifas.ufl.edu/data/reports/?res",
#  "referrerPolicy": "no-referrer-when-downgrade",
#  "body": "
# locs__260=on&
# locs__304=on&
# locs__390=on&
# reportType=daily&  "all" for 15 minute, "hourly" for hourly, "monthly" for monthly
# presetRange=dates&
# fromDate_m=8&
# fromDate_d=25&
# fromDate_y=2020&
# toDate_m=9&
# toDate_d=23&
# toDate_y=2020&
# vars__AirTemp1=on&
# vars__AirTemp9=on&
# vars__AirTemp15=on&
# vars__SoilTempAvg=on&
# vars__DewPoint=on&
# vars__WetBulb=on&
# vars__RelHumAvg=on&
# vars__Rainfall=on&
# vars__TotalRad=on&
# vars__WindSpeed=on&
# vars__WindDir=on&
# vars__ET=on&
# vars__BP=on&
# format=HTML+table",
#  "method": "POST",
#  "mode": "cors",
#  "credentials": "include"

# FAWN https://fawn.ifas.ufl.edu/

locs__ = {
    260: ["alachua"],
    320: ["apopka"],
    490: ["arcadia"],
    304: ["avalon"],
    350: ["balm"],
    410: ["belle glade", "belle_glade", "belleglade"],
    230: ["bronson"],
    310: ["brooksville"],
    150: ["carrabelle"],
    250: ["citra"],
    405: ["clewiston"],
    311: ["dade city", "dade_city", "dadecity"],
    120: ["defuniak springs", "defuniak_springs", "defuniaksprings"],
    360: ["dover"],
    420: [
        "fort lauderdale",
        "fort_lauderdale",
        "fortlauderdale",
        "ft lauderdale",
        "ft. lauderdale",
        "ftlauderdale",
        "ft.lauderdale",
    ],
    390: ["frostproof"],
    430: [
        "fort pierce",
        "fort_pierce",
        "fortpierce",
        "ft. pierce",
        "ft pierce",
        "ftpierce",
        "ft.pierce",
    ],
    270: ["hastings"],
    440: ["homestead"],
    450: ["immokalee"],
    371: ["indian river", "indian_river", "indianriver"],
    110: ["jay"],
    241: ["joshua"],
    340: ["kenansville"],
    330: ["lake alfred", "lake_alfred", "lakealfred"],
    275: ["lecanto"],
    170: ["live oak", "live_oak", "liveoak"],
    180: ["macclenny"],
    130: ["marianna"],
    121: ["mayo"],
    160: ["monticello"],
    480: ["north port"],
    280: ["ocklawaha"],
    303: ["okahumpka"],
    455: ["okeechobee"],
    380: ["ona"],
    460: ["palmdale"],
    290: ["pierson"],
    240: ["putnam hall", "putnam_hall", "putnamhall"],
    140: ["quincy"],
    470: ["sebring"],
    435: [
        "st. lucie west",
        "st._lucie_west",
        "st_lucie_west",
        "saint_lucie_west",
        "st.luciewest",
        "stluciewest",
    ],
    302: ["umatilla"],
    425: ["wellington"],
}

rev_locs = {}
for key in locs__:
    rev_locs[key] = key
    rev_locs[str(key)] = key
    for i in locs__[key]:
        rev_locs[i.lower()] = key

# variable names for stations are "loc__XXX" where XXX is one of the keys
# above.

reportTypes = ["all", "hourly", "daily", "monthly", "entire"]

vars__ = {
    "AirTemp1": ["airtemp@60cm", "airtemp1"],
    "AirTemp9": ["airtemp@2m", "airtemp9"],
    "AirTemp15": ["airtemp@10m", "airtemp15"],
    "SoilTempAvg": ["soiltempavg"],
    "DewPoint": ["dewpoint"],
    "WetBulb": ["wetbulb"],
    "RelHumAvg": ["relhumavg"],
    "Rainfall": ["rainfall"],
    "TotalRad": ["totalrad"],
    "WindSpeed": ["windspeed"],
    "WindDir": ["winddir"],
    "ET": ["et"],
    "BP": ["bp"],
}

rev_vars = {}
for key in vars__:
    rev_vars[key] = key
    for i in vars__[key]:
        rev_vars[i] = key

# new_units_table = [
#     [
#         "{0}\n{1}".format(i, placeholder._UNITS_MAP[i][0]),
#         "{0}".format(placeholder._UNITS_MAP[i][1]),
#     ]
#     for i in placeholder._UNITS_MAP
# ]

# units_table = tb(
#     new_units_table,
#     tablefmt="grid",
#     headers=['fawn "variable" string Description', "Units"],
# )

# units_table = "\n".join(["        {0}".format(i) for i in units_table.split("\n")])


@mando.command("fawn", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def fawn_cli(
    stations, variables, reportType, start_date=None, end_date=None,
):
    r"""Download data from Florida Automated Weather Network (FAWN).

    Parameters
    ----------
    stations :  str

        At the command line can supply a comma separated list or codes or
        names.  Using the Python API needs to be a Python list.

        The current complete list of FAWN stations.

        * 260  Alachua
        * 320  Apopka
        * 490  Arcadia
        * 304  Avalon
        * 350  Balm
        * 410  'Belle Glade'
        * 230  Bronson
        * 310  Brooksville
        * 150  Carrabelle
        * 250  Citra
        * 405  Clewiston
        * 311  'Dade City'
        * 120  'Defuniak Springs'
        * 360  Dover
        * 420  'Fort Lauderdale'
        * 390  Frostproof
        * 430  'Fort Pierce'
        * 270  Hastings
        * 440  Homestead
        * 450  Immokalee
        * 371  'Indian River'
        * 110  Jay
        * 241  Joshua
        * 340  Kenansville
        * 330  'Lake Alfred'
        * 275  Lecanto
        * 170  'Live Oak'
        * 180  Macclenny
        * 130  Marianna
        * 121  May
        * 160  Monticello
        * 480  'North Port'
        * 280  Ocklawaha
        * 303  Okahumpka
        * 455  Okeechobee
        * 380  Ona
        * 460  Palmdale
        * 290  Pierson
        * 240  Putnam Hall
        * 140  Quincy
        * 470  Sebring
        * 435  'St. Lucie West'
        * 302  Umatilla
        * 425  Wellington

    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list.

        The current complete list of FAWN variables are:

        +-------------+-------------------------------------+--------+
        | Name        | Description                         | Units  |
        +=============+=====================================+========+
        | AirTemp1    | Air temperature at 60 cm            | degF   |
        +-------------+-------------------------------------+--------+
        | AirTemp9    | Air temperature at 2 m              | degF   |
        +-------------+-------------------------------------+--------+
        | AirTemp15   | Air temperature at 10 m             | degF   |
        +-------------+-------------------------------------+--------+
        | SoilTempAvg | Soil temperature at -10 cm          | degF   |
        +-------------+-------------------------------------+--------+
        | DewPoint    | Dew point                           | degF   |
        +-------------+-------------------------------------+--------+
        | WetBulb     | Wet bulb temperature                | degF   |
        +-------------+-------------------------------------+--------+
        | RelHumAvg   | Relative humidity                   |        |
        +-------------+-------------------------------------+--------+
        | Rainfall    | Rainfall                            | in     |
        +-------------+-------------------------------------+--------+
        | TotalRad    | Total solar radiation               | w/m2   |
        +-------------+-------------------------------------+--------+
        | WindSpeed   | Wind speed                          | mph    |
        +-------------+-------------------------------------+--------+
        | WindDir     | Wind direction                      | degree |
        +-------------+-------------------------------------+--------+
        | ET          | Reference ET Penman-Monteith        | in     |
        +-------------+-------------------------------------+--------+
        | BP          | Barometric pressure at 2 m          | mb     |
        +-------------+-------------------------------------+--------+

        The 'ET' variable is only available when `reportType` is "daily" or
        "monthly".
    reportType : str
        Interval of the data.  Can be one of "all" for 15 minute, "hourly",
        "daily", or "monthly".
    {start_date}
    {end_date}
    """
    tsutils._printiso(
        fawn(stations, variables, reportType, start_date=start_date, end_date=end_date,)
    )


def core(data):
    """Download a chunk of data."""
    br = mechanize.Browser()
    br.open("https://fawn.ifas.ufl.edu/data/reports/")
    br.select_form(nr=0)
    for key in data:
        if "locs__" in key or "vars__" in key:
            br.form.toggle_single(type="checkbox", name=key)
    br.form["presetRange"] = ["dates"]
    br.form["fromDate_y"] = [str(data["fromDate_y"])]
    br.form["fromDate_m"] = [str(data["fromDate_m"])]
    br.form["fromDate_d"] = [str(data["fromDate_d"])]
    br.form["toDate_y"] = [str(data["toDate_y"])]
    br.form["toDate_m"] = [str(data["toDate_m"])]
    br.form["toDate_d"] = [str(data["toDate_d"])]
    response = br.submit(nr=1)

    df = pd.read_csv(response, index_col=[0, 1], parse_dates=True)
    return df


@tsutils.validator(
    stations=[
        [str.lower, ["domain", list(rev_locs.keys())], None],
        [int, ["domain", list(locs__.keys())], None],
    ],
    variables=[str, ["domain", list(vars__.keys()) + list(rev_vars.keys())], None],
    reportType=[str, ["domain", ["all", "hourly", "daily", "monthly"]], 1],
    start_date=[tsutils.parsedate, ["pass", []], 1],
    end_date=[tsutils.parsedate, ["pass", []], 1],
)
def fawn(
    stations, variables, reportType, start_date=None, end_date=None,
):
    r"""Download data from FAWN."""
    interval = {"all": 30, "hourly": 366, "daily": 732, "monthly": 3660}
    data = {}
    try:
        data["start_date"] = tsutils.parsedate(start_date)
    except KeyError:
        data["start_date"] = datetime.datetime(1998, 1, 1)
    try:
        data["end_date"] = tsutils.parsedate(end_date)
    except KeyError:
        data["end_date"] = datetime.now()

    for station in tsutils.make_list(stations):
        try:
            data["locs__{0}".format(rev_locs[station])] = "on"
        except KeyError:
            try:
                data["locs__{0}".format(rev_locs[station.lower()])] = "on"
            except KeyError:
                raise ValueError(
                    tsutils.error_wrapper(
                        """
Station {station} is not in the list of stations.
                                 """.format(
                            **locals()
                        )
                    )
                )

    for variable in tsutils.make_list(variables):
        try:
            data["vars__{0}".format(rev_vars[variable])] = "on"
        except KeyError:
            raise ValueError(
                tsutils.error_wrapper(
                    """
Variable {variable} is not available.
""".format(
                        **locals()
                    )
                )
            )

    ndf = pd.DataFrame()

    sdate = tsutils.parsedate(data["start_date"])
    edate = tsutils.parsedate(data["end_date"])
    _ = data.pop("start_date")
    _ = data.pop("end_date")

    testdate = sdate
    while testdate < edate:

        begin_test_date = tsutils.parsedate(testdate)
        data["fromDate_m"] = begin_test_date.month
        data["fromDate_d"] = begin_test_date.day
        data["fromDate_y"] = begin_test_date.year

        testdate = testdate + pd.Timedelta(days=interval[reportType])
        if testdate > edate:
            testdate = edate

        end_test_date = tsutils.parsedate(testdate)
        data["toDate_m"] = end_test_date.month
        data["toDate_d"] = end_test_date.day
        data["toDate_y"] = end_test_date.year

        df = core(data)
        # With multi-index pandas won't combine_first with an empty ndf.
        if len(ndf) == 0:
            ndf = df
        else:
            ndf = ndf.combine_first(df)

    if len(ndf) == 0:
        raise ValueError(
            tsutils.error_wrapper(
                """
FAWN service returned no values for stations "{stations}", variables "{variables}"
between "{sdate}" and "{edate}".
""".format(
                    **locals()
                )
            )
        )

    try:
        ndf.drop(columns="N (# obs)", inplace=True)
    except KeyError:
        pass

    def renamer(istr):
        istr = istr.replace(" ", "")
        istr = istr.replace("(", ":")
        istr = istr.replace(")", ":")
        return istr

    ndf = ndf.unstack(level="FAWN Station")
    ndf.rename(columns=renamer, inplace=True)
    ndf = ndf.swaplevel(axis="columns")
    ndf.columns = ["_".join(tup).rstrip("_") for tup in ndf.columns.values]
    return ndf


fawn.__doc__ = fawn_cli.__doc__


if __name__ == "__main__":
    r = fawn(
        stations="260,120,180,240",
        variables="WindDir",
        reportType="daily",
        start_date="2000-01-01",
        end_date="2003-01-01",
    )
    print(r)

    r = fawn(
        stations="260,120,180,240",
        variables="rainfall,winddir",
        reportType="daily",
        start_date="2017-01-01",
        end_date="2020-01-01",
    )
    print(r)

    r = fawn(
        stations="Alachua,MacClenny",
        variables="Rainfall,AirTemp9",
        reportType="daily",
        start_date="2000-01-01",
        end_date="2003-01-01",
    )
    print(r)
