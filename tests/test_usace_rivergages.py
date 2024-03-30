import datetime

import test_util

from tsgettoolbox import ulmo


def test_get_stations():
    stations_file = "usace/rivergages/get_stations.cfm"
    with test_util.mocked_urls(stations_file):
        stations = ulmo.usace.rivergages.get_stations()
    assert len(stations) > 1500
    assert "CE7F42E6" in stations


def test_get_station_parameters():
    test_sets = [
        ("CE7F42E6", {"HP": "Pool Level (Ft)", "PC": "Cumulative Precipitation (In)"})
    ]

    for station_code, test_value in test_sets:
        stations_file = f"usace/rivergages/parameters_{station_code}.cfm"
        with test_util.mocked_urls(stations_file):
            parameters = ulmo.usace.rivergages.get_station_parameters(station_code)

        assert parameters == test_value


def test_get_station_data():
    test_sets = [
        (
            "CE7F42E6",
            [(datetime.date(2013, 1, 1), 168.04), (datetime.date(2013, 1, 15), 168.69)],
        )
    ]

    for station_code, test_values in test_sets:
        stations_file = f"usace/rivergages/data_{station_code}.cfm"
        with test_util.mocked_urls(stations_file):
            station_data = ulmo.usace.rivergages.get_station_data(
                "CE7F42E6", "HP", start="2013-1-1", end="2013-1-15"
            )

        for test_value in test_values:
            assert test_value in iter(station_data.items())
