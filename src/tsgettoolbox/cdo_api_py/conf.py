API_HOST_URL = "https://www.ncdc.noaa.gov/cdo-web"
API_VERSION = "v2"
DATETIME_FMT_SHORT = "%Y-%m-%d"
DATETIME_FMT_LONG = "%Y-%m-%dT%H:%M:%S"
ENDPOINTS = {
    "datasets": "A dataset is the primary grouping for data at NCDC",
    "datacategories": "A data category is a general type of data used to group similar data types.",
    "datatypes": "A data type is a specific type of data that is often unique to a dataset.",
    "locationcategories": "A location category is a grouping of similar locations.",
    "locations": "A location is a geopolitical entity.",
    "stations": "A station is a any weather observing platform where data is recorded.",
    "data": "A datum is an observed value along with any ancillary attributes at a specific place and time.",
}

year = 365
decade = 3650
DATASET_MAX_RANGES = {
    "GHCND": year,
    "GSOM": decade,
    "GSOY": decade,
    "NEXRAD2": year,
    "NEXRAD3": year,
    "NORMAL_ANN": decade,
    "NORMAL_DLY": year,
    "NORMAL_HLY": year,
    "NORMAL_MLY": decade,
    "PRECIP_15": year,
    "PRECIP_HLY": year,
}
