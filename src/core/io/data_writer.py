import numpy as np
import rasterio
from rasterio.transform import from_bounds


def save_bands_to_geotiff(
    bands: dict[str, np.ndarray], bbox: tuple, filepath: str
):
    """
    Saves the fetched bands into a multi-band GeoTIFF file.

    Args:
        bands: A dictionary with band names as keys and numpy arrays as values.
        bbox: A tuple representing the bounding box (west, south, east, north).
        filepath: The path where the GeoTIFF file will be saved.
    """
    required_bands = ["B04", "B08", "B11"]
    if not all(b in bands for b in required_bands):
        raise ValueError(
            f"Missing one of the required bands: {required_bands}"
        )

    first_band = bands[required_bands[0]]
    height, width = first_band.shape
    dtype = first_band.dtype
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
        dst.set_band_description(1, "B04 - Red")
        dst.set_band_description(2, "B08 - NIR")
        dst.set_band_description(3, "B11 - SWIR")
    print(f"💾 Data successfully saved to: {filepath}")