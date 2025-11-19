import csv
import os
import time
from urllib.request import Request, urlopen

import pandas as pd
from bs4 import BeautifulSoup

_ndict = {}


def read_url(url):
    url = url.replace(" ", "%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, "html.parser")
    x = soup.find_all("a")
    for i in x:
        file_name = i.extract().get_text()
        url_new = url + file_name
        url_new = url_new.replace(" ", "%20")
        if file_name[-1] == "/" and file_name[0] != ".":
            read_url(url_new)
        year = os.path.dirname(url_new)
        year = os.path.basename(year)
        try:
            year = int(year)
        except ValueError:
            continue
        key = os.path.basename(url_new)
        if ".csv" not in key:
            continue
        _ndict.setdefault(key, []).append(year)
        print(key, year)


csv_columns = ["stationid", "start_year", "end_year"]

read_url("https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/")

for nkey in _ndict:
    _ndict[nkey] = [_ndict[nkey][0], _ndict[nkey][-1]]

sod_stations = _ndict.keys()

with open("gsod_stations.dat", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for key, data in _ndict.items():
        writer.writerow({"stationid": key, "start_year": data[0], "end_year": data[1]})

sod_df = pd.read_csv("gsod_stations.dat")
sod_df = sod_df.sort_values(by=["stationid"])
sod_df.to_csv("gsod_stations.dat", index=False)

_ndict = {}


def read_monthly_url(url):
    url = url.replace(" ", "%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, "html.parser")
    x = soup.find_all("a")
    for i in x:
        time.sleep(1)
        file_name = i.extract().get_text()
        url_new = url + file_name
        url_new = url_new.replace(" ", "%20")
        if ".csv" not in file_name:
            continue
        df = pd.read_csv(url_new, header=0, parse_dates=["DATE"])
        _ndict.setdefault(file_name, []).append(f"{min(df['DATE'])}")
        _ndict.setdefault(file_name, []).append(f"{max(df['DATE'])}")
        print(file_name, min(df["DATE"]), max(df["DATE"]))


read_monthly_url("https://www.ncei.noaa.gov/data/global-summary-of-the-month/access/")

for nkey in _ndict:
    _ndict[nkey] = [_ndict[nkey][0], _ndict[nkey][-1]]

som_stations = _ndict.keys()

with open("gsom_stations.dat", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for key, data in _ndict.items():
        writer.writerow({"stationid": key, "start_year": data[0], "end_year": data[1]})

som_df = pd.read_csv("gsom_stations.dat")
som_df = som_df.sort_values(by=["stationid"])
som_df.to_csv("gsom_stations.dat", index=False)
