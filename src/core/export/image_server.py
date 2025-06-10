import rasterio
import numpy as np

def save_geotiff(filepath: str, data: np.ndarray, profile: dict):
    """Zapisz wynik jako GeoTIFF"""
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw'
    )
    with rasterio.open(filepath, 'w', **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)