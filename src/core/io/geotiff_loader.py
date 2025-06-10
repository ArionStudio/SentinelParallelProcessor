import rasterio
import numpy as np
from typing import Tuple

def load_band(filepath: str) -> Tuple[np.ndarray, dict]:
    """Wczytaj jedno pasmo z pliku GeoTIFF"""
    with rasterio.open(filepath) as src:
        band = src.read(1).astype(np.float32)
        profile = src.profile
    return band, profile