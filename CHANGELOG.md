## v23.22.2 (2022-03-26)

### Fix

- **twc.py**: removed debugging print statements
- **ncei.py**: corrected factor for ncei_ghcnd_ftp
- **cdec.py**: fixed filtering of station parameters
- **opendap**: fixed and improved speed for all pydap downloads

## v23.22.1 (2022-02-14)

## v23.22.0 (2022-02-14)

### Feat

- **docstrings**: use new dostring template format in latest tstoolbox

## v23.21.3 (2022-02-07)

### Fix

- misc fixes

## v23.21.2 (2021-12-16)

## v23.21.1 (2021-12-16)

## v23.21.0 (2021-12-15)

### Fix

- misc
- pip_requirements.txt to reduce vulnerabilities

### Feat

- added rivergages and swtwc from the USACE

## v23.20.1 (2021-11-24)

### Fix

- misc import fixes and removal of zeep and tables dependencies
- minor edits while going through code to make sure "tables" package isn't used
- **usgs_eddn**: removed usgs_eddn since no longer available
- **nwis_gwlevels**: unstacked on "site_no" and no longer set time zone name in "Datetime" title

## v23.20.0 (2021-11-22)

### Feat

- added ncei_ish and improved ncei download using the cdo-api-py library

## v23.19.0 (2021-11-15)

### Feat

- **ncei**: parallelized downloads for all NCEI CDO sources
- replaced xarray/pydap with siphon and made opendap downloads multi-threaded
- **metdata**: added many new observation datasets by using thredds.northwestknowledge.net instead of usgs cida

## v23.18.1 (2021-10-05)

### Fix

- **epa_wqp**: countycode and statecode included in epa_wqp function

## vv23.18.0 (2021-09-07)

### Fix

- reset version number in pyproject.toml so the 'cz bump' would work correctly

## v23.16.1 (2021-09-07)

### Fix

- reset version numbers so 'cz bump' works

## v23.16.0 (2021-09-07)

### Fix

- **MANIFEST.in**: added correct path to include pmcodes.dat which is required by nwis_* subcommands

## vusgs_flet (2021-08-21)

### Feat

- **usgs_flet.py**: renamed usgs_whets and split into usgs_flet_stns and usgs_flet_narr

## v23.15.8 (2021-08-01)

## v23.15.7 (2021-07-25)

## v23.15.6 (2021-07-24)

## v23.14.6 (2021-07-22)

### Fix

- netcdf4 dep., docs

## v23.13.6 (2021-07-07)

### Fix

- Finished some part of terraclimate
fix: rename ncdc to ncei
fix: ldas deprecated "variable" in favor of "variables"
fix: ncei 1/10 degC to full degC
fix: ncei allow for prefix or no prefix for variables
fix: ncei add units to column header.
docs: misc.

### Refactor

- Apply all tests in .pre-commmit-config.yaml
feat: Add metdata.

## v23.11.5 (2021-06-10)

### Fix

- various small fixes.

## v23.10.5 (2021-05-19)

### Feat

- Added usgs_whets pull from USGS-CIDA
fix: Minor fixes for ncei and fawn

## v22.10.5 (2021-05-14)

### Fix

- The rolling download feature of ncdc/ncei now works correctly.
refactor: Renamed all "ncdc" to "ncei" to match name change from
National Climatic Data Center, to National Centers for Environmental
Information.
docs: Small fixes for the ncdc -> ncei name change
style: Removed all trailing spaces and used "black" to reformat.

## v22.9.4 (2021-05-12)

### Fix

- Better defaults in xr.open_dataset
- Made metdata variables a keyword.

## v22.8.4 (2021-05-07)

### Feat

- Added metdata download.

## v21.8.4 (2021-03-14)

### Fix

- Now will co

## v21.7.4 (2021-03-06)

### Feat

- Allow for multiple variables in ldas.

## v21.6.4 (2021-03-06)

### Fix

- Make Literal work with Python 3.6.7.

## v21.5.4 (2021-03-06)

### Fix

- Requests now retries. Better docs. typic.al
- Removing remnants of "odo".

### Perf

- Removed dependence on "odo".

## v21.4.4 (2021-02-11)

### Fix

- fawn-handled empty responses.

## v21.3.4 (2021-02-11)

### Fix

- Fixed start and end dates in fawn.
- Testing of station names was incorrect.

## v21.2.3 (2021-02-01)

### Fix

- Spelling errors/mechanize is new dependency

### Feat

- Added FAWN support.

## v21.1.2 (2020-09-05)

### Fix

- Bunch of miscellaneous fixes.
- Added units to column names for cpc.
- Updated to latest URL for cdec
- COOPS now uses https.

## v21.1.1 (2020-04-30)

## v20.42.11.23 (2020-03-28)

## v20.42.11.22 (2020-03-09)

## v20.42.11.21 (2020-03-09)

## v20.41.11.21 (2019-11-20)

## v18.39.11.21 (2019-11-02)

## v17.38.11.21 (2019-10-21)

## v17.38.11.20 (2019-10-03)

## v17.38.11.18 (2019-09-18)
