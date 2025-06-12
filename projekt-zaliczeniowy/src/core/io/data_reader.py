# src/core/io/data_reader.py
import numpy as np
import rasterio
from typing import Dict


def read_geotiff_bands(filepath: str) -> Dict[str, np.ndarray]:
    """
    ZMIANA: Odczytuje 4 pasma z GeoTIFF, w tym dataMask.
    """
    print(f"📖 Reading data from cached file: {filepath}")
    with rasterio.open(filepath) as src:
        # Zakładamy, że zapisaliśmy pasma w tej kolejności
        bands = {
            "B04": src.read(1),
            "B08": src.read(2),
            "B11": src.read(3),
            # ZMIANA: Odczytujemy dataMask z 4. pasma
            "dataMask": src.read(4)
        }
        return bands