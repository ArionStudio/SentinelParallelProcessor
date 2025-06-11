import numpy as np
import rasterio
from rasterio.transform import from_bounds
from multiprocessing import Pool, cpu_count
from typing import Tuple
import matplotlib.pyplot as plt

def _compute_indices_tile(args):
    b4_tile, b8_tile, b11_tile = args
    ndvi = np.zeros_like(b4_tile, dtype=np.float32)
    ndmi = np.zeros_like(b4_tile, dtype=np.float32)

    denom_ndvi = b8_tile + b4_tile
    denom_ndmi = b8_tile + b11_tile

    np.divide(b8_tile - b4_tile, denom_ndvi, out=ndvi, where=denom_ndvi != 0)
    np.divide(b8_tile - b11_tile, denom_ndmi, out=ndmi, where=denom_ndmi != 0)

    return ndvi, ndmi

def calculate_and_save_indices_parallel(
    input_tif_path: str,
    ndvi_output_path: str,
    ndmi_output_path: str,
    n_jobs: int = None
):
    """
    Oblicza NDVI i NDMI z trójkanałowego pliku GeoTIFF (B04, B08, B11)
    i zapisuje je do oddzielnych plików.

    Args:
        input_tif_path: Ścieżka do wejściowego pliku GeoTIFF z pasmami B04, B08, B11.
        ndvi_output_path: Ścieżka do zapisu pliku NDVI.
        ndmi_output_path: Ścieżka do zapisu pliku NDMI.
        n_jobs: Liczba procesów równoległych (domyślnie: liczba rdzeni CPU).
    """
    with rasterio.open(input_tif_path) as src:
        b4 = src.read(1).astype(np.float32)
        b8 = src.read(2).astype(np.float32)
        b11 = src.read(3).astype(np.float32)
        bbox = src.bounds
        height, width = b4.shape
        transform = from_bounds(*bbox, width, height)

    if n_jobs is None:
        n_jobs = cpu_count()

    b4_chunks = np.array_split(b4, n_jobs, axis=0)
    b8_chunks = np.array_split(b8, n_jobs, axis=0)
    b11_chunks = np.array_split(b11, n_jobs, axis=0)

    with Pool(n_jobs) as pool:
        results = pool.map(_compute_indices_tile, zip(b4_chunks, b8_chunks, b11_chunks))

    ndvi = np.vstack([r[0] for r in results])
    ndmi = np.vstack([r[1] for r in results])

    # Zapis wyników
    for data, path, desc in zip(
        [ndvi, ndmi],
        [ndvi_output_path, ndmi_output_path],
        ["NDVI", "NDMI"]
    ):
        with rasterio.open(
            path, "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype=np.float32,
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(data, 1)
        print(f"💾 Saved {desc} to {path}")

    with rasterio.open("ndvi_output.tif") as src:
        ndvi = src.read(1)
        print("Rozmiar:", ndvi.shape)
        print("Typ danych:", ndvi.dtype)
        print("Zakres wartości:", ndvi.min(), "→", ndvi.max())
    
    plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(label="NDVI")
    plt.title("NDVI Heatmap")
    plt.show()

if __name__ == "__main__":
    calculate_and_save_indices_parallel(
        input_tif_path="sentinel_data.tif",
        ndvi_output_path="ndvi_output.tif",
        ndmi_output_path="ndmi_output.tif",
        n_jobs=4  # lub domyślnie: CPU count
    )
