import csv
import os
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from tsgettoolbox import utils

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


csv_columns = ["stationid", "year"]

read_url("https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/")

for nkey in _ndict:
    _ndict[nkey] = [_ndict[nkey][0], _ndict[nkey][-1]]

with open("gsod_stations.dat", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data in _ndict:
        writer.writerow(data)

_ndict = {}
read_url("https://www.ncei.noaa.gov/data/global-summary-of-the-month/access/")

for nkey in _ndict:
    _ndict[nkey] = [_ndict[nkey][0], _ndict[nkey][-1]]

with open("gsom_stations.dat", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data in _ndict:
        writer.writerow(data)

# Read in API key
api_key = utils.read_api_key("ncei_cdo")
headers = {"token": api_key}

s = utils.requests_retry_session()
ireq = Request(
    "GET",
    r"http://www.ncdc.noaa.gov/cdo-web/api/v2/stations/",
    headers=headers,
)
prepped = ireq.prepare()
dreq = s.send(prepped)
dreq.raise_for_status()

data_file = open("jsonoutput.csv", "w", newline="")
csv_writer = csv.writer(data_file)

count = 0
for data in dreq.json():
    if count == 0:
        header = data.keys()
        csv_writer.writerow(header)
        count += 1
    csv_writer.writerow(data.values())

data_file.close()
