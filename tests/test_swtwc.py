import datetime
import importlib


def _response_with_swtwc_data():
    text = "\n".join(
        [
            "Station ABCD Example Station",
            "Station Type: RESERVOIR",
            "Note: Example note",
            "",
            f"{'':11}{'STAGE':<10}",
            f"{'':11}{'FT':<10}",
            f"{'':11}{'USACE':<10}",
            "(CST)",
            f"{'06/09 12:00':<14}{'123.4':>10}",
        ]
    )

    class Response:
        content = f"<html><body><pre>{text}</pre></body></html>".encode()

    return Response()


def _assert_station_data(module, monkeypatch):
    monkeypatch.setattr(
        module.requests, "get", lambda *args, **kwargs: _response_with_swtwc_data()
    )

    result = module.get_station_data("ABCD", date="2024-06-09", as_dataframe=True)

    dataframe = result["values"]
    assert result["code"] == "ABCD"
    assert dataframe.index[0] == datetime.datetime(2024, 6, 9, 12, 0)
    assert dataframe.loc[datetime.datetime(2024, 6, 9, 12, 0), "STAGE"] == 123.4


def test_functions_swtwc_get_station_data_parses_dates(monkeypatch):
    module = importlib.import_module("tsgettoolbox.functions.swtwc")
    _assert_station_data(module, monkeypatch)


def test_ulmo_swtwc_get_station_data_parses_dates(monkeypatch):
    module = importlib.import_module("tsgettoolbox.ulmo.usace.swtwc.core")
    _assert_station_data(module, monkeypatch)
