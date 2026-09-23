# Third party imports
import async_retriever as ar

# First party imports
from tsgettoolbox import utils

netrc_key = "api.waterdata.usgs.gov"
email, token = utils.read_netrc(netrc_key)

dbases = [
    "agency-codes",
    "altitude-datums",
    "aquifer-codes",
    "aquifer-types",
    "channel-measurements",
    "citations",
    "combined-metadata",
    "continuous",
    "coordinate-accuracy-codes",
    "coordinate-datum-codes",
    "coordinate-method-codes",
    "counties",
    "countries",
    "daily",
    "field-measurements-metadata",
    "field-measurements",
    "hydrologic-unit-codes",
    "latest-continuous",
    "latest-daily",
    "latest-field-measurements",
    "medium-codes",
    "method-categories",
    "method-citations",
    "methods",
    "monitoring-locations",
    "national-aquifer-codes",
    "parameter-codes",
    "peaks",
    "reliability-codes",
    "site-types",
    "states",
    "statistic-codes",
    "time-series-metadata",
    "time-series-methods",
    "time-series-revisions",
    "time-zone-codes",
    "topographic-codes",
]

urls = [
    f"https://api.waterdata.usgs.gov/ogcapi/v0/collections/{func_name}/queryables"
    for func_name in dbases
]

respons = ar.retrieve_text(
    urls, [{"params": {"f": "json"}, "headers": {"X-Api-Key": token}}] * len(urls)
)

fnames = [f"{func_name}_queryables.json" for func_name in dbases]

for fname, resp in zip(fnames, respons):
    with open(fname, "w", encoding="utf-8") as f:
        f.write(resp)
