# scripts/run_memory_tests.py

import os
import json
from memory_profiler import memory_usage

# --- Konfiguracja ---
TEST_DATA_DIR = "test_data/scaled"
RESULTS_FILE = "test_results/memory_results.json"
TEST_FILE_SIZE = 1024

def run_gpu_calculation(bands_data, index_type):
    from src.core.processing.index_calculator import calculate_index
    calculate_index(bands_data, index_type)

def run_cpu_single_calculation(bands_data, index_type):
    from src.core.processing.cpu_single_thread_calculator import calculate_index
    calculate_index(bands_data, index_type)

def run_cpu_multi_calculation(bands_data, index_type, n_jobs):
    from src.core.processing.cpu_index_calculator import calculate_index
    calculate_index(bands_data, index_type, n_jobs=n_jobs)

def run_profiling():
    from src.core.io.data_reader import read_geotiff_bands
    from multiprocessing import cpu_count, freeze_support
    
    freeze_support()

    test_file = os.path.join(TEST_DATA_DIR, f"scaled_data_{TEST_FILE_SIZE}.tif")
    if not os.path.exists(test_file):
        print(f"BŁĄD: Plik testowy {test_file} nie istnieje.")
        print("Uruchom najpierw 'python -m src.scripts.generate_scaled_data'.")
        return

    print(f"Wczytuję dane testowe z pliku: {test_file}")
    bands = read_geotiff_bands(test_file)
    index_type = "NDVI"
    
    results = {}
    # Only include thread counts up to cpu_count()
    max_threads = cpu_count()
    cpu_threads_to_test = sorted(set(t for t in [1, 2, 4, 8, 16, max_threads] if t <= max_threads))

    # Test GPU
    print("\n" + "="*50 + "\n PROFILOWANIE PAMIĘCI: GPU (Taichi)\n" + "="*50)
    mem_usage = memory_usage((run_gpu_calculation, (bands, index_type)), interval=0.1, timeout=200)
    results['GPU (Taichi)'] = max(mem_usage)
    print(f"Peak memory usage: {max(mem_usage):.2f} MiB")

    # Test CPU Single
    print("\n" + "="*50 + "\n PROFILOWANIE PAMIĘCI: CPU (1-Thread, NumPy)\n" + "="*50)
    mem_usage = memory_usage((run_cpu_single_calculation, (bands, index_type)), interval=0.1, timeout=200)
    results['CPU (1-Thread, NumPy)'] = max(mem_usage)
    print(f"Peak memory usage: {max(mem_usage):.2f} MiB")

    # Testy CPU Multi
    for threads in cpu_threads_to_test:
        label = f'CPU ({threads}-Threads, SharedMem)'
        print("\n" + "="*50 + f"\n PROFILOWANIE PAMIĘCI: {label}\n" + "="*50)
        mem_usage = memory_usage((run_cpu_multi_calculation, (bands, index_type, threads)), interval=0.1, timeout=200)
        results[label] = max(mem_usage)
        print(f"Peak memory usage (main process): {max(mem_usage):.2f} MiB")

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\nWyniki profilowania pamięci zostały zapisane w: {RESULTS_FILE}")

if __name__ == "__main__":
    run_profiling()