import numpy as np
import rasterio
from rasterio.enums import Resampling
from multiprocessing import Pool, cpu_count


def calculate_ndvi_block(b):
    red, nir = b[0], b[1]
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = (nir - red) / (nir + red)
    return np.clip(ndvi, -1, 1)


def process_ndvi_parallel(tiff_path: str, output_path: str):
    with rasterio.open(tiff_path) as src:
        red = src.read(1, resampling=Resampling.nearest).astype(np.float32)
        nir = src.read(2, resampling=Resampling.nearest).astype(np.float32)

    h, w = red.shape
    blocks = cpu_count()
    chunk_h = h // blocks
    slices = [(red[i*chunk_h:(i+1)*chunk_h], nir[i*chunk_h:(i+1)*chunk_h]) for i in range(blocks)]

    with Pool(blocks) as p:
        ndvi_chunks = p.map(calculate_ndvi_block, slices)

    ndvi = np.vstack(ndvi_chunks)

    profile = src.profile
    profile.update(dtype=rasterio.float32, count=1)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)
