# src/core/io/data_writer.py
import numpy as np
import rasterio
from rasterio.transform import from_bounds


def save_bands_to_geotiff(
    bands: dict[str, np.ndarray], bbox: tuple, filepath: str
):
    """
    ZMIANA: Zapisuje 4 pasma (B04, B08, B11, dataMask) do GeoTIFF.
    """
    # ZMIANA: Wymagamy teraz również dataMask
    required_bands = ["B04", "B08", "B11", "dataMask"]
    if not all(b in bands for b in required_bands):
        raise ValueError(
            f"Missing one of the required bands: {required_bands}"
        )

    first_band = bands[required_bands[0]]
    height, width = first_band.shape
    dtype = first_band.dtype
    # ZMIANA: Liczba pasm to teraz 4
    count = len(required_bands)

    west, south, east, north = bbox
    transform = from_bounds(west, south, east, north, width, height)

    with rasterio.open(
        filepath,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=count,
        dtype=dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(bands["B04"], 1)
        dst.write(bands["B08"], 2)
        dst.write(bands["B11"], 3)
        # ZMIANA: Zapisujemy dataMask jako 4. pasmo
        dst.write(bands["dataMask"], 4)
        
        dst.set_band_description(1, "B04 - Red")
        dst.set_band_description(2, "B08 - NIR")
        dst.set_band_description(3, "B11 - SWIR")
        dst.set_band_description(4, "dataMask")

    print(f"💾 Data successfully saved to: {filepath}")