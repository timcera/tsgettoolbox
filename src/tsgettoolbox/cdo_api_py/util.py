from typing import List, Optional


def _make_geojson_point_feature(
    properties: Optional[dict] = None, coordinates: Optional[list] = None
):
    """
    Creates a geojson format feature.

    :param properties: dictionary with the properties for the feature.
    :param coordinates: The point features coordinates in [ lon, lat ] format.
    :return:
    """
    # fill empty properties with blank id property.
    if properties is None:
        properties = {"id": None}

    if not isinstance(coordinates, list):
        raise Exception  # more specific
    if len(coordinates) != 2:
        raise Exception  # more specific

    point_feature = {
        "type": "Feature",
        "properties": properties,  # Attributes go here!
        "geometry": {
            "type": "Point",
            "coordinates": coordinates,  # Coordinates go here! contains [lon, lat] pair
        },
    }

    return point_feature


def _make_geojson_layer(features: List[dict], name: str):
    """
    :param features: List of geojson compliant dictionaries.
    :param name: The name attribute for the layer.
    :return:
    """
    # A geojson layer form looks like this.
    feature_layer = {
        "type": "FeatureCollection",
        "name": name,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": features,
    }
    return feature_layer


def rows_to_point_geojson(
    rows: List[dict], name: str, lat_key: str = "latitude", lon_key: str = "longitude"
) -> dict:
    """
    A tabular dataset with lat-lon pairs for each row can be converted into
    a feature class point layer. A dataframe to dictionaries with a "records"
    orientation, or otherwise created list of dictionaries for each feature of
    the feature layer is suitable. Function intended for use in converting
    table of weather stations to a GIS format.

    Example use:

        ``` python
        from pathlib import Path
        import pandas as pd
        import geojson

        # read a previously saved csv of weather stations
        df = pd.read_csv("ghcnd_stations.csv", index_col=0)

        # convert to geojson dictionary
        station_geojson = rows_to_point_geojson(
            df.to_dict(orient="records"), name="ghcnd_stations"
        )

        # serialize it to a geojson file.
        with Path("ghcnd_stations.geojson").open("w+") as f:
            f.write(geojson.dumps(station_geojson, indent=4))
        ```

    :param rows: List of dictionaries, every dictionary must have an entry for lat_key and lon_key.
    :param name: name to give the feature class layer
    :param lat_key: string key used to find latitude values in rows dictionaries
    :param lon_key: string key used to find longitude values in row dictionaries.

    :return: a dictionary serializable to geojson with geojson.dumps()
    """
    features = []

    for row in rows:
        if lon_key not in row:
            raise KeyError(f"{lon_key}, not found in row [{row}]")

        if lat_key not in row:
            raise KeyError(f"{lat_key}, not found in row [{row}]")

        row_coords = [row[lon_key], row[lat_key]]
        row_feature = _make_geojson_point_feature(
            properties=row, coordinates=row_coords
        )
        features.append(row_feature)

    feature_layer = _make_geojson_layer(features, name=name)
    return feature_layer
