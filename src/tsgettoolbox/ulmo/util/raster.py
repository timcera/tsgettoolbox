"""
ulmo.util.raster
~~~~~~~~~~~~~~~~

Collection of useful functions for raster manipulation
"""

import hashlib
import os
import zipfile

from .misc import download_if_new, mkdir_if_doesnt_exist


def mosaic_and_clip(raster_tiles, xmin, ymin, xmax, ymax, output_path):
    import subprocess

    import rasterio
    from pyproj import Proj

    print("Mosaic and clip to bounding box extents")
    output_vrt = f"{os.path.splitext(output_path)[0]}.vrt"
    print(
        subprocess.check_output(
            ["gdalbuildvrt", "-overwrite", output_vrt] + raster_tiles
        )
    )
    # check crs
    with rasterio.drivers():
        with rasterio.open(output_vrt) as src:
            p = Proj(src.crs)

    if not p.is_latlong():
        [xmax, xmin], [ymax, ymin] = p([xmax, xmin], [ymax, ymin])

    print(
        subprocess.check_output(
            [
                "gdalwarp",
                "-overwrite",
                "-te",
                repr(xmin),
                repr(ymin),
                repr(xmax),
                repr(ymax),
                output_vrt,
                output_path,
            ]
        )
    )
    print("Output raster saved at %s", output_path)


def download_tiles(path, tile_urls, tile_fmt, check_modified=False):
    raster_tiles = []

    if isinstance(tile_urls, str):
        tile_urls = [tile_urls]

    for i, url in enumerate(tile_urls):
        filename = os.path.split(url)[-1]
        print(f"... downloading tile {i + 1} of {len(tile_urls)} from {url}")
        mkdir_if_doesnt_exist(path)
        mkdir_if_doesnt_exist(os.path.join(path, "zip"))
        tile_path = os.path.join(path, filename)
        if tile_fmt == "":
            download_if_new(url, tile_path, check_modified=check_modified)
        else:
            zip_path = os.path.join(path, "zip", filename)
            download_if_new(url, zip_path, check_modified=check_modified)
            print(f"... ... zipfile saved at {zip_path}")
            tile_path = extract_from_zip(zip_path, tile_path, tile_fmt)

        raster_tiles.append(tile_path)
    return raster_tiles


def extract_from_zip(zip_path, tile_path, tile_fmt):
    tile_path = os.path.splitext(tile_path)[0] + tile_fmt
    with zipfile.ZipFile(zip_path) as z:
        fname = [x for x in z.namelist() if tile_fmt in x[-4:]][0]
        with open(tile_path, "wb") as f:
            f.write(z.read(fname))
            print(f"... ... {tile_fmt} format raster saved at {tile_path}")

    return tile_path


def generate_raster_uid(layer, xmin, ymin, xmax, ymax):
    return hashlib.md5(
        ",".join([layer, repr(xmin), repr(ymin), repr(xmax), repr(ymax)])
    ).hexdigest()
