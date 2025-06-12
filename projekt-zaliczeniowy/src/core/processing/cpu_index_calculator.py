# src/core/processing/cpu_index_calculator.py

import numpy as np
from multiprocessing import cpu_count
from multiprocessing.shared_memory import SharedMemory
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Tuple

global_shared_arrays = {}


def _init_worker(info: Dict):
    global global_shared_arrays
    for key, item in info.items():
        shm = SharedMemory(name=item["name"])
        global_shared_arrays[key] = np.ndarray(
            item["shape"], dtype=item["dtype"], buffer=shm.buf
        )
        global_shared_arrays[f"{key}_shm_ref"] = shm


def _process_chunk(chunk_info: Tuple[int, int, str]):
    start_row, end_row, index_type = chunk_info

    b8 = global_shared_arrays["B08"]

    if index_type == "NDVI":
        b4 = global_shared_arrays["B04"]
        output_arr = global_shared_arrays["output_NDVI"]

        b4_tile = b4[start_row:end_row]
        b8_tile = b8[start_row:end_row]

        denominator = b8_tile + b4_tile
        result_tile = np.divide(
            b8_tile - b4_tile,
            denominator,
            where=denominator > 1e-6,
            out=np.zeros_like(b4_tile),
        )
        output_arr[start_row:end_row] = result_tile

    elif index_type == "NDMI":
        b11 = global_shared_arrays["B11"]
        output_arr = global_shared_arrays["output_NDMI"]

        b8_tile = b8[start_row:end_row]
        b11_tile = b11[start_row:end_row]

        denominator = b8_tile + b11_tile
        result_tile = np.divide(
            b8_tile - b11_tile,
            denominator,
            where=denominator > 1e-6,
            out=np.zeros_like(b8_tile),
        )
        output_arr[start_row:end_row] = result_tile


def calculate_index(
    bands: Dict[str, np.ndarray], index_type: str, n_jobs: int = None
) -> Tuple[np.ndarray, np.ndarray]:
    if n_jobs is None:
        n_jobs = cpu_count()

    # ZMIANA: Bardziej precyzyjny komunikat w logach
    print(
        f"Starting calculation for: {index_type} using CPU ({n_jobs} processes, Shared Memory)..."
    )

    data_mask = bands["dataMask"]
    input_arrays = {"B08": bands["B08"].astype(np.float32)}
    if index_type == "NDVI":
        input_arrays["B04"] = bands["B04"].astype(np.float32)
        output_name = "output_NDVI"
        h, w = input_arrays["B04"].shape
    elif index_type == "NDMI":
        input_arrays["B11"] = bands["B11"].astype(np.float32)
        output_name = "output_NDMI"
        h, w = input_arrays["B08"].shape
    else:
        raise ValueError(f"Nieznany typ wskaźnika: {index_type}")

    shm_list = []
    worker_info = {}
    try:
        for name, arr in input_arrays.items():
            shm = SharedMemory(create=True, size=arr.nbytes)
            shared_arr = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)
            shared_arr[:] = arr[:]
            shm_list.append(shm)
            worker_info[name] = {
                "name": shm.name,
                "shape": arr.shape,
                "dtype": arr.dtype,
            }

        output_arr_template = np.zeros((h, w), dtype=np.float32)
        shm_out = SharedMemory(create=True, size=output_arr_template.nbytes)
        worker_info[output_name] = {
            "name": shm_out.name,
            "shape": output_arr_template.shape,
            "dtype": output_arr_template.dtype,
        }
        shm_list.append(shm_out)

        row_indices = np.array_split(np.arange(h), n_jobs)
        tasks = [
            (chunk[0], chunk[-1] + 1, index_type)
            for chunk in row_indices
            if len(chunk) > 0
        ]

        with ProcessPoolExecutor(
            max_workers=n_jobs, initializer=_init_worker, initargs=(worker_info,)
        ) as executor:
            list(executor.map(_process_chunk, tasks))

        final_result = np.copy(
            np.ndarray(
                output_arr_template.shape,
                dtype=output_arr_template.dtype,
                buffer=shm_out.buf,
            )
        )

        return final_result, data_mask

    finally:
        for shm in shm_list:
            shm.close()
            shm.unlink()