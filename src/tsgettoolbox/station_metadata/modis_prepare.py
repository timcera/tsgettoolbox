import json

import numpy as np
import pandas as pd
import requests
from tabulate import tabulate

products_url = "https://modis.ornl.gov/rst/api/v1/products?tool=GlobalSubset"
r = requests.get(products_url).text
r = json.loads(r)
pdf = pd.json_normalize(r, record_path=["products"])
pdf = pdf.set_index("product")

ndesc = pdf["description"].str.split(")", expand=True)
pdf["description"] = f"{ndesc[0]})"
pdf.columns = ["Description", "Frequency", "Resolution\n(m)"]
print(
    tabulate(pdf, tablefmt="grid", maxcolwidths=[None, 25, None, None], headers="keys")
)

rename = {
    "description": "Description",
    "fill_value": "Missing",
    "add_offset": "Offset",
    "scale_factor": "Scale",
    "units": "Units",
    "valid_range": "Range",
}

fill_value = {}
scale_factor = {}
add_offset = {}
units = {}
valid_range = {}
for prod in pdf.index:
    band_url = f"https://modis.ornl.gov/rst/api/v1/{prod}/bands"
    r = requests.get(band_url).text
    r = json.loads(r)
    bdf = pd.json_normalize(r, record_path=["bands"])
    bdf = bdf.set_index("band")

    bdf["units"] = bdf["units"].replace("na", "")
    bdf["units"] = bdf["units"].replace("none", "")
    bdf["units"] = bdf["units"].replace("days since 1-1-1970", "days_since_1970-01-01")
    bdf["units"] = bdf["units"].replace("Mg ha-1", "Mg/ha")
    bdf["units"] = bdf["units"].replace("bit field", "bit_field")
    bdf["units"] = bdf["units"].replace("mW m-2 nm-1 sr-1", "mW/m2/nm/sr")
    bdf["units"] = bdf["units"].replace("Kelvin", "degK")
    bdf["units"] = bdf["units"].replace("Julian day of the year", "day_of_year")
    bdf["units"] = bdf["units"].replace("NoUnits", "")
    bdf["units"] = bdf["units"].replace("reflectance- no units", "")
    bdf["units"] = bdf["units"].replace("no units", "")
    bdf["units"] = bdf["units"].replace("day of year", "day_of_year")
    bdf["units"] = bdf["units"].replace("number of days", "number_of_days")
    bdf["units"] = bdf["units"].replace(np.nan, "")
    bdf["units"] = bdf["units"].str.replace(" per ", "/")
    bdf["units"] = bdf["units"].str.replace("ratio ", "ratio_")
    bdf["units"] = bdf["units"].str.replace(".*No units", "", regex=True)
    bdf["units"] = bdf["units"].replace("Julian day", "day_of_year")
    bdf["units"] = bdf["units"].replace("dimensionless", "")
    bdf["description"] = bdf["description"].str.replace("_", " ")

    if "valid_range" in bdf.columns:
        for val in bdf.itertuples():
            testval = val.valid_range.split(" to ")
            valid_range[val.Index] = [int(i) for i in testval]
        bdf["valid_range"] = bdf["valid_range"].str.replace(" to ", " to\n")
    if "fill_value" in bdf.columns:
        for val in bdf.itertuples():
            try:
                testval = val.fill_value
                if testval:
                    fill_value[val.Index] = int(val.fill_value)
            except ValueError:
                pass
    if "units" in bdf.columns:
        for val in bdf.itertuples():
            if val.units:
                units[val.Index] = val.units
    if "scale_factor" in bdf.columns:
        for val in bdf.itertuples():
            try:
                testval = float(val.scale_factor)
                if testval != 1 and testval is not np.nan:
                    scale_factor[val.Index] = float(val.scale_factor)
            except ValueError:
                pass
    if "add_offset" in bdf.columns:
        for val in bdf.itertuples():
            try:
                testval = float(val.add_offset)
                if testval != 0 and testval is not np.nan:
                    add_offset[val.Index] = float(val.add_offset)
            except ValueError:
                pass

    bdf = bdf.convert_dtypes()

    bdf = bdf.rename(rename, axis="columns")
    bdf = bdf.drop(["Missing", "Scale", "Offset"], axis="columns", errors="ignore")

    cwidths = [None] * len(bdf.columns)
    cwidths[1] = 30
    print()
    print(prod)
    print()
    print(tabulate(bdf, tablefmt="grid", headers="keys", maxcolwidths=cwidths))

print(f"{fill_value=}")
print(f"{scale_factor=}")
print(f"{add_offset=}")
print(f"{units=}")
print(f"{valid_range=}")
