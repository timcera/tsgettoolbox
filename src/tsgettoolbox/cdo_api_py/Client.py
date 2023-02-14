from datetime import datetime, timedelta
from time import sleep
from warnings import warn

import pandas as pd
import requests

from .conf import (
    API_HOST_URL,
    API_VERSION,
    DATASET_MAX_RANGES,
    DATETIME_FMT_LONG,
    DATETIME_FMT_SHORT,
    ENDPOINTS,
)
from .exceptions import *


class BaseClient:
    """
    The base client has only the most basic functions at the core of
    interfacing with the API
    """

    def __init__(self, token, backup_token=None, verify_token=False):
        self.token = token
        self.backup_token = backup_token
        self.headers = {
            "token": token,
            "Content-Type": "application/json;charset=UTF-8",
        }
        self.host = API_HOST_URL
        self.version = API_VERSION
        self.verbose = True
        self.n_api_calls = 0

        if verify_token:
            valid, response = self._test_auth()
            if not valid:
                raise AuthError(response.json()["message"])

    def _test_auth(self):
        r = self._get("datasets")
        if r.status_code == 400:
            return False, r
        return True, r

    @staticmethod
    def _segment_daterange(start, end, maxdelta):
        """
        Segments a date range into shorter pieces with 'maxdelta' length.
        :param start: starting datetime
        :param end:  ending datetime
        :param maxdelta: timedelta instance representing max time window
        :return:
        """
        cur = start
        while cur < end:
            yield (cur, min(cur + maxdelta, end))
            cur += maxdelta

    @staticmethod
    def _validate_endpoint(endpoint):
        """Compares endpoint against a list of valid endpoints"""
        if endpoint in ENDPOINTS:
            return True
        raise InvalidEndpoint(
            f"Endpoint '{endpoint}' is invalid! valid options are {ENDPOINTS.keys()}"
        )

    @staticmethod
    def _format_extent(extent):
        """if input extent looks like an extent dictionary, return extent formatted string"""
        if isinstance(extent, dict):
            if all(d in extent for d in ("south", "north", "west", "east")):
                return '{extent["south"]}, {extent["west"]}, {extent["north"]}, {extent["east"]}'
            raise BadExtentError(
                f"{extent} does not appear to have all keys north, south, east, west"
            )

        if isinstance(extent, str):
            coords = [float(c) for c in extent.split(",")]
            if len(coords) == 4:
                return coords
            raise BadExtentError(
                f"extent must contain the four n,s,e,w coordinates. got {extent}"
            )
        raise BadExtentError(f"Could not interpret or verify extent input {extent}")

    def _format_datetime_as_string(self, item):
        """
        Ensures datetime objects are formatted as acceptable strings. Uses
        short format for datetimes with no hours minutes seconds. returns items which
        are not either datetimes, or lists of datetimes, unaltered.
        """
        if isinstance(item, datetime):
            if all(
                [
                    item.hour == 0,
                    item.minute == 0,
                    item.second == 0,
                    item.microsecond == 0,
                ]
            ):
                return item.strftime(DATETIME_FMT_SHORT)
            return item.strftime(DATETIME_FMT_LONG)

        if isinstance(item, list):
            return [self._format_datetime_as_string(sub_item) for sub_item in item]
        return item

    def _parse_string_to_datetime(self, string, ignore_invalid=False):
        """
        parses a string and returns a datetime object. will work on either long or short formats

        :param string: input string to be formated to datetime
        :param ignore_invalid: set to True to simply return the string if it could not be converted.
                               set to False to raise an error if a string cannot be converted.
        """

        def validate(string, date_format):
            try:
                return datetime.strptime(string, date_format)
            except ValueError:
                return False

        if isinstance(string, str):
            long = validate(string, DATETIME_FMT_LONG)
            short = validate(string, DATETIME_FMT_SHORT)
            if long:
                return long
            if short:
                return short
            if ignore_invalid:
                return string
            raise InvalidDatestring(
                f'input datestring "{string}" does not match acceptable formats "{DATETIME_FMT_LONG}" or "{DATETIME_FMT_SHORT}"'
            )

        if isinstance(string, list):
            return [self._parse_string_to_datetime(s) for s in string]

        if isinstance(string, datetime):
            return string

        raise TypeError(f"input {string} is not of valid type to parse date string")

    def _url_builder(self, endpoint, *args, **kwargs):
        """
        Formats an api call url from args and host info, passing None's is OK.
        keyword arguments can be anything supported by the endpoint.
        """
        self._validate_endpoint(endpoint)
        baseurl = "/".join([self.host, "api", self.version, endpoint, *args])
        if kwargs:
            joins = []
            for k, v in kwargs.items():
                if v is not None:  # ignore none values from undefined kwargs
                    v = self._format_datetime_as_string(
                        v
                    )  # ensure datetimes are formatted properly
                    if (
                        k == "extent"
                    ):  # ensure formatting if an extent argument is passed
                        v = self._format_extent(v)
                    if isinstance(v, list):  # handles multiple value arguments
                        joins += [f"{k}={vv}" for vv in v]
                    else:
                        joins.append(f"{k}={v}")
            url = f"{baseurl}?{'&'.join(joins)}"
        else:
            url = baseurl
        if self.verbose:
            print(url)
        return url

    def _get(self, url):
        """Sends a get request to the url with authentication token attached in the header"""
        r = requests.get(url=url, headers=self.headers)
        self.n_api_calls += 1
        if r.status_code == 429:
            message = r.json()["message"]
            if "per second" in message:
                raise RequestsPerSecondLimitExceeded(message)
            if "per day" in message:
                raise RequestsPerDayLimitExceeded(message)
        elif r.status_code == 400:
            raise Request400Error(r.json()["message"])
        elif r.status_code == 502:
            raise Request502Error("502 bad gateway")
        return r


class Client(BaseClient):
    """
    This client assists greatly with creating one or more requests to return
    all relevant data to the user.
    """

    def __init__(self, token, default_limit=1000, default_units=None):
        super().__init__(token=token)
        self.default_limit = default_limit
        self.default_units = default_units

    # ====== endpoint list methods.

    @staticmethod
    def list_endpoints():
        return ENDPOINTS

    def list_datasets(self):
        return self.squash_results(self.get("datasets"))

    def list_datacategories(self):
        return self.squash_results(self.get("datacategories"))

    def list_datatypes(self):
        return self.squash_results(self.get("datatypes"))

    def list_locationcategories(self):
        return self.squash_results(self.get("locationcategories"))

    def list_locations(self):
        return self.squash_results(self.get("locations"))

    def list_stations(self):
        return self.squash_results(self.get("stations"))

    # ====== Get request modifiers and checkers

    def _get_with_url_builder(self, endpoint, *args, **kwargs):
        """Passes args to url assembler and sends get request to that url"""
        self._validate_endpoint(endpoint)
        url = self._url_builder(endpoint, *args, **kwargs)
        return self._get(url)

    def _get_with_count_checks(self, endpoint, *args, **kwargs):
        """
        If the first response indicates the count is greater than the limit, it modifies
        the offset argument and sends another request until all items have been obtained.
        yields responses as they are obtained.

        Invoked by '_get_with_request_checks', invokes '_get_with_url_builder'
        """
        response = self._get_with_url_builder(endpoint, *args, **kwargs)
        yield response

        # if the response hits the limit, send more requests and yield responses
        if response.status_code == 200:
            resp_json = response.json()
            if "metadata" in resp_json.keys():
                meta = resp_json["metadata"]["resultset"]
                offset = 0
                limit = meta["limit"]
                count = meta["count"]
                while offset + limit < count:
                    offset += limit
                    kwargs["offset"] = offset
                    kwargs["limit"] = limit
                    yield self._get_with_url_builder(endpoint, *args, **kwargs)

    def _get_with_request_checks(self, endpoint, *args, **kwargs):
        """
        Manages '_get' requests. Keeps API calls to 5 per second and segments
        requests when the responses are very long. Because multiple requests
        may be required, this is a generator object that yields the responses.

        Invoked by 'get', invokes '_get_with_count_checks'
        """

        try:
            yield from self._get_with_count_checks(endpoint, *args, **kwargs)

        except RequestsPerSecondLimitExceeded:
            sleep(1.2)  # a little extra margin
            yield from self._get_with_request_checks(endpoint, *args, **kwargs)
        except RequestsPerDayLimitExceeded:
            if self.backup_token is not None:
                warn(
                    "Daily limit exceeded for primary token! Switching to backup token!"
                )
                self.token = self.backup_token
                yield from self.get(endpoint, **kwargs)
            else:
                print("Try using a backup token next time!")
                raise
        # except Request502Error:
        #     sleep(1)
        #     yield from self._get_with_request_checks(endpoint, *args, **kwargs)

    def get(
        self, endpoint, *args, datasetid=None, startdate=None, enddate=None, **kwargs
    ):
        """
        Highest level get function that splits requests into many requests as
        required according to the various API restrictions listed below. The
        getter then returns a generator object which will have one or more
        response objects in it.

        API call limit: the API accepts 5 calls per second, if an error is encountered
                        due to reaching this limit, the get is delayed by 1 second and tried
                        again.

        Count limit:    the API response will include no more than 1000 items, but includes
                        the total number of results in the response. This number is read,
                        and if it is greater than the limit, a new request is automatically
                        generated for the next 1000 items, continuously.

        Date limit:     Most data products limit requests to span one year of time, others
                        limit to a decade. The datasetid, startdate, and enddate arguments
                        are checked for this criteria, and if they exceed the maximum date
                        range, the request is broken up into smaller requests of allowable
                        date range length.

        :param datasetid: a valid datasetid from the options available. see list_datasets()
        :param startdate: a datetime object bounding the minimum date to cover
        :param enddate: a datetime object bounding the maximum date to cover
        :param kwargs: any other keyword arguments accepted by the API.
        """
        if "limit" not in kwargs:
            if self.default_limit is not None:
                kwargs["limit"] = self.default_limit
        if "units" not in kwargs:
            if self.default_units is not None:
                kwargs["units"] = self.default_units

        if endpoint == "data":  # special date restrictions apply to data endpoint!
            for arg in (datasetid, startdate, enddate):
                if arg is None:
                    raise RequiredArgumentError(
                        f"Calls to 'data' endpoint require '{arg}' keyword argument!"
                    )

            max_range = timedelta(days=DATASET_MAX_RANGES[datasetid])
            for start, end in self._segment_daterange(startdate, enddate, max_range):
                # assemble new kwargs by modifying dates and adding user kwargs
                get_args = dict(
                    datasetid=datasetid,
                    startdate=start.strftime(DATETIME_FMT_SHORT),
                    enddate=end.strftime(DATETIME_FMT_SHORT),
                    **kwargs,
                )
                yield from self._get_with_request_checks(endpoint, *args, **get_args)
        else:
            # combine the defined kwargs with the undefined ones
            get_args = dict(
                datasetid=datasetid, startdate=startdate, enddate=enddate, **kwargs
            )
            yield from self._get_with_request_checks(endpoint, *args, **get_args)

    # ===== Data fetchers and formaters

    @staticmethod
    def squash_results(responses):
        """
        Extracts the results from a list of response objects and returns a list
        of just the results.
        """
        results = []
        for r in responses:
            try:
                r_json = r.json()
                if "results" in r_json.keys():
                    results += r.json()["results"]
            except:
                print(f"Warning: could not squash response: \n {r}, {r.content}")
        return results

    @staticmethod
    def results_to_dataframe(results, include_attributes=False):
        """creates a pandas dataframe from a list of common results"""
        if len(results) > 0:
            df = pd.DataFrame(results)
            if len(df) > 0:  # pivot tables can't be formed on empty dataframes
                if include_attributes is True:
                    df = df.pivot_table(
                        values=df.columns.drop(["datatype", "date", "station"]),
                        index=["station", "date"],
                        columns="datatype",
                        aggfunc="first",
                    )
                    df.columns = [
                        "_".join(tuple(map(str, col))).rstrip("_")
                        for col in df.columns.values
                    ]
                    df = df.rename(columns=lambda x: x.replace("value_", ""))
                else:
                    df = df.pivot_table(
                        values="value", index=["station", "date"], columns="datatype"
                    )
                return df
        return pd.DataFrame()

    def find_stations(
        self,
        datasetid,
        extent,
        startdate=None,
        enddate=None,
        return_dataframe=True,
        **kwargs,
    ):
        """
        Returns list of stations within input bounding box.

        :param datasetid: one of the datasetids (see list_datasets())
        :param extent: dict with south, west, north and east keys. values in decimal degrees.
        :param startdate: startdate api argument (datetime)
        :param enddate: enddate api argument (datetime)
        :param return_dataframe: set to True to return a pandas dataframe.
        :return:
        """
        results = self.squash_results(
            self.get(
                "stations",
                datasetid=datasetid,
                extent=self._format_extent(extent),
                startdate=startdate,
                enddate=enddate,
                **kwargs,
            )
        )

        if return_dataframe:
            return pd.DataFrame(results)
        return results

    def lookup_station(self, stationid):
        """
        look up station metadata by station id
        :param stationid: known station id
        """
        # result squashing wont work for station lookups, different dictionary keys
        response = list(self.get("stations", stationid))[0]
        return response.json()

    def get_data_by_station(
        self,
        datasetid,
        stationid,
        startdate=None,
        enddate=None,
        return_dataframe=True,
        include_station_meta=False,
        include_attributes=False,
        **kwargs,
    ):
        """
        Gets weather station data for given inputs. datasetid and stationid are
        the only required inputs. startdate and enddate will be set to fetch
        all data available for that stationid if left None.

        :param datasetid: required, see list_datasets() for options.
        :param stationid: required, station id. use find_stations() to help with this.
        :param startdate: datetime object for startdate of data query window.
        :param enddate: datetime object for enddate of data query window.
        :param return_dataframe: use True to return pandas dataframe of results
        :param include_station_meta: Set True to include lat,lon,elevation of station in results.
        :param kwargs: optional keyword arguments for get() call.
        :return: list of dicts with get results or pandas dataframe as per 'return_dataframe'
        """
        # only lookup station metadata if it is needed to conserve API calls.
        if startdate is None or enddate is None or include_station_meta:
            station_meta = self.lookup_station(stationid)

            if startdate is None:
                startdate = self._parse_string_to_datetime(station_meta["mindate"])
            if enddate is None:
                enddate = self._parse_string_to_datetime(station_meta["maxdate"])
        else:
            station_meta = None

        responses = list(
            self.get(
                "data",
                datasetid=datasetid,
                stationid=stationid,
                startdate=startdate,
                enddate=enddate,
                **kwargs,
            )
        )

        results = self.squash_results(responses)

        # return_dataframe or not, the best way to grapple this data is with a dataframe
        data_df = self.results_to_dataframe(
            results, include_attributes=include_attributes
        ).reset_index()

        if include_station_meta:  # merge metadata into data_df
            meta_df = pd.DataFrame(station_meta, index=[0])
            data_df = pd.merge(data_df, meta_df, left_on="station", right_on="id")
            del data_df["id"]  # this is duplicated with 'station'

        if return_dataframe:
            return data_df
        return list(data_df.to_dict("index").values())
