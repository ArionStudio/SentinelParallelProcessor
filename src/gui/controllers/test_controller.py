# src/gui/controllers/test_controller.py

import os
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, List, Dict, Tuple
from tkinter import messagebox
from multiprocessing import cpu_count

from src.core.io.data_reader import read_geotiff_bands
from src.core.io.test_writer import save_test_results
from src.core.io.test_reader import load_test_results
from src.core.processing.index_calculator import calculate_index as calculate_index_gpu
from src.core.processing.cpu_index_calculator import calculate_index as calculate_index_cpu_multi
from src.core.processing.cpu_single_thread_calculator import calculate_index as calculate_index_cpu_single
from src.gui.utils import visualizer

if TYPE_CHECKING:
    from src.gui.app import MainApplication
    from src.gui.views.test_view import TestView

class TestController:
    TEST_DATA_DIR = "test_data/scaled"
    RESULTS_FILE = "test_results/full_report_results.json"
    MEMORY_RESULTS_FILE = "test_results/memory_results.json"
    CHARTS_DIR = "report/charts"
    REPETITIONS = 5
    CPU_SCALABILITY_THREADS = sorted(list(set([1, 2, 4, 8, cpu_count()])))
    STANDARD_TEST_SIZE = 1024

    def __init__(self, app: "MainApplication"):
        self.app = app
        self.view: "TestView" | None = None
        os.makedirs(self.CHARTS_DIR, exist_ok=True)

    def set_view(self, view: "TestView"):
        self.view = view

    def handle_run_tests(self):
        if not self.view: return
        self.view.set_buttons_state(False)
        self.view.clear_results()
        thread = threading.Thread(target=self._run_tests_worker, daemon=True)
        thread.start()

    def handle_generate_full_report(self):
        if not self.view: return
        self.view.clear_results()
        self.view.update_progress(0, "Loading all available results...")

        time_results = load_test_results(self.RESULTS_FILE)
        memory_results = load_test_results(self.MEMORY_RESULTS_FILE)

        if not time_results:
            messagebox.showerror("Error", f"Could not find time results file: {self.RESULTS_FILE}\nPlease run the tests first.")
            if self.view and self.view.winfo_exists():
                self.view.update_progress(100, "Ready.")
            return

        all_figures, all_descriptions = self._generate_all_plots(time_results, memory_results)
        
        if self.view and self.view.winfo_exists():
            if all_figures:
                self.view.display_results(all_figures, all_descriptions)
                self.view.update_progress(100, "Full report generated and charts saved.")
            else:
                self.view.update_progress(100, "No data found to generate a report.")

    def _run_tests_worker(self):
        try:
            # ZMIANA: Dodano blok walidacji plików i folderów na początku
            # 1. Sprawdź, czy główny folder z danymi testowymi istnieje
            if not os.path.isdir(self.TEST_DATA_DIR):
                error_msg = f"Test data directory not found:\n\n{os.path.abspath(self.TEST_DATA_DIR)}\n\nPlease create it and add scaled GeoTIFF files."
                self.app.after(0, messagebox.showerror, "Setup Error", error_msg)
                if self.view and self.view.winfo_exists():
                    self.app.after(0, self.view.update_progress, 100, "Error: Test data directory missing.")
                return

            # 2. Sprawdź, czy folder zawiera jakiekolwiek pliki .tif do testów skalowalności
            test_files = sorted(
                [f for f in os.listdir(self.TEST_DATA_DIR) if f.endswith('.tif')],
                key=lambda x: int(x.split('_')[-1].split('.')[0])
            )
            if not test_files:
                error_msg = f"No test files (.tif) found in:\n\n{os.path.abspath(self.TEST_DATA_DIR)}\n\nPlease add scaled GeoTIFF files to run the tests."
                self.app.after(0, messagebox.showerror, "Setup Error", error_msg)
                if self.view and self.view.winfo_exists():
                    self.app.after(0, self.view.update_progress, 100, "Error: No test files found.")
                return

            # 3. Sprawdź, czy istnieje konkretny plik wymagany do testów skalowalności CPU
            cpu_test_file_path = os.path.join(self.TEST_DATA_DIR, f"scaled_data_{self.STANDARD_TEST_SIZE}.tif")
            if not os.path.exists(cpu_test_file_path):
                error_msg = f"Required file for CPU scaling test is missing:\n\n{os.path.basename(cpu_test_file_path)}\n\nPlease ensure this file exists in the test directory."
                self.app.after(0, messagebox.showerror, "Setup Error", error_msg)
                if self.view and self.view.winfo_exists():
                    self.app.after(0, self.view.update_progress, 100, "Error: CPU test file missing.")
                return

            # Jeśli wszystkie testy przeszły, kontynuuj
            if self.view and self.view.winfo_exists():
                self.app.after(0, self.view.update_progress, 0, "Test environment OK. Starting tests...")
            
            all_results = {'scalability': {}, 'cpu_scaling': {}, 'gpu_overhead': {}}
            
            num_scalability_runs = len(test_files) * self.REPETITIONS * 3
            num_cpu_scaling_runs = len(self.CPU_SCALABILITY_THREADS) * self.REPETITIONS
            total_steps = (num_scalability_runs + num_cpu_scaling_runs) * 2
            completed_steps = 0

            for index_type in ["NDVI", "NDMI"]:
                all_results['scalability'][index_type] = {}
                all_results['cpu_scaling'][index_type] = {}
                all_results['gpu_overhead'][index_type] = {}

                # Testy skalowalności (w zależności od rozmiaru danych)
                for file_name in test_files:
                    size = int(file_name.split('_')[-1].split('.')[0])
                    size_key = str(size)
                    all_results['scalability'][index_type][size_key] = {}
                    file_path = os.path.join(self.TEST_DATA_DIR, file_name)
                    bands_data = read_geotiff_bands(file_path)

                    for config_label, func, kwargs in [
                        ('GPU (Taichi)', calculate_index_gpu, {}),
                        ('CPU (1-Thread, NumPy)', calculate_index_cpu_single, {}),
                        (f'CPU ({max(self.CPU_SCALABILITY_THREADS)})-Threads, SharedMem)', calculate_index_cpu_multi, {'n_jobs': max(self.CPU_SCALABILITY_THREADS)})
                    ]:
                        times = []
                        for i in range(self.REPETITIONS):
                            status = f"Testing {index_type} Scalability on {size}x{size} ({config_label}, Rep {i+1})"
                            if self.view and self.view.winfo_exists():
                                self.app.after(0, self.view.update_progress, (completed_steps/total_steps)*100, status)
                            else:
                                print("Test view closed, aborting tests.")
                                return
                            times.append(self._time_execution(func, bands_data, index_type, **kwargs))
                            completed_steps += 1
                        all_results['scalability'][index_type][size_key][config_label] = times
                        if config_label == 'GPU (Taichi)' and size == self.STANDARD_TEST_SIZE:
                            all_results['gpu_overhead'][index_type] = times
                        save_test_results(all_results, self.RESULTS_FILE)

                # Testy skalowalności CPU (w zależności od liczby wątków)
                bands_data_cpu = read_geotiff_bands(cpu_test_file_path)
                for threads in self.CPU_SCALABILITY_THREADS:
                    times = []
                    for i in range(self.REPETITIONS):
                        status = f"Testing {index_type} CPU Scaling with {threads} threads (Rep {i+1})"
                        if self.view and self.view.winfo_exists():
                            self.app.after(0, self.view.update_progress, (completed_steps/total_steps)*100, status)
                        else:
                            print("Test view closed, aborting tests.")
                            return
                        times.append(self._time_execution(calculate_index_cpu_multi, bands_data_cpu, index_type, n_jobs=threads))
                        completed_steps += 1
                    all_results['cpu_scaling'][index_type][f'{threads}-Threads'] = times
                    save_test_results(all_results, self.RESULTS_FILE)

            if self.view and self.view.winfo_exists():
                self.app.after(0, self.view.update_progress, 100, "All tests finished. Generating full report...")
                self.app.after(0, self.handle_generate_full_report)

        except Exception as e:
            error_message = f"An unexpected error occurred during testing: {e}"
            if self.view and self.view.winfo_exists():
                self.view.update_progress(100, error_message)
                messagebox.showerror("Runtime Error", error_message)
        finally:
            if self.view and self.view.winfo_exists():
                self.app.after(0, self.view.set_buttons_state, True)

    def _time_execution(self, func, *args, **kwargs) -> float:
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time

    def _generate_all_plots(self, time_results: Dict, memory_results: Dict) -> Tuple[List[plt.Figure], List[str]]:
        all_figures, all_descriptions = [], []
        
        # Wykres 1: Przegląd wydajności
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        fig1.suptitle(f"Performance Overview ({self.STANDARD_TEST_SIZE}x{self.STANDARD_TEST_SIZE} data)", fontsize=16)
        labels = ['GPU (Taichi)', 'CPU (1-Thread, NumPy)', f'CPU ({max(self.CPU_SCALABILITY_THREADS)})-Threads, SharedMem)']
        ndvi_times = [np.mean(time_results['scalability']['NDVI'][str(self.STANDARD_TEST_SIZE)][l]) * 1000 for l in labels]
        ndmi_times = [np.mean(time_results['scalability']['NDMI'][str(self.STANDARD_TEST_SIZE)][l]) * 1000 for l in labels]
        x = np.arange(len(labels)); width = 0.35
        rects1 = ax1.bar(x - width/2, ndvi_times, width, label='NDVI'); rects2 = ax1.bar(x + width/2, ndmi_times, width, label='NDMI')
        ax1.set_ylabel('Average Time (ms)'); ax1.set_xticks(x); ax1.set_xticklabels(labels, rotation=10); ax1.legend()
        ax1.bar_label(rects1, padding=3, fmt='%.1f'); ax1.bar_label(rects2, padding=3, fmt='%.1f')
        fig1.savefig(os.path.join(self.CHARTS_DIR, "01_performance_overview.png"), dpi=300)
        all_figures.append(fig1); all_descriptions.append("This chart provides the main performance overview. For a standard dataset, the optimized single-thread NumPy implementation is the fastest due to low overhead. The GPU is slower because of data transfer costs, and the parallel CPU is hampered by process management overhead.")
        plt.close(fig1)

        # Wykres 2: Skalowalność CPU
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        fig2.suptitle("CPU Parallelization Scalability", fontsize=16)
        cpu_times_ndvi = [np.mean(time_results['cpu_scaling']['NDVI'][f'{t}-Threads']) * 1000 for t in self.CPU_SCALABILITY_THREADS]
        ax2.plot(self.CPU_SCALABILITY_THREADS, cpu_times_ndvi, marker='o', linestyle='-', label='Parallel CPU Time (NDVI)')
        single_thread_time = np.mean(time_results['scalability']['NDVI'][str(self.STANDARD_TEST_SIZE)]['CPU (1-Thread, NumPy)']) * 1000
        ax2.axhline(y=single_thread_time, color='gray', linestyle='--', label=f'Optimized Single-Thread Time ({single_thread_time:.1f} ms)')
        ax2.set_xlabel('Number of Processes'); ax2.set_ylabel('Average Time (ms)'); ax2.set_xticks(self.CPU_SCALABILITY_THREADS); ax2.legend(); ax2.grid(True)
        fig2.savefig(os.path.join(self.CHARTS_DIR, "02_cpu_scalability.png"), dpi=300)
        all_figures.append(fig2); all_descriptions.append("This chart analyzes the parallel CPU performance. The blue line shows that adding more processes reduces execution time, proving the implementation scales. However, it also shows that the parallel version starts with a high time cost (overhead) and never becomes faster than the superior, non-parallel single-thread approach (gray line) for this task.")
        plt.close(fig2)

        # Wykres 3 i 4: Skalowalność vs. Rozmiar Danych
        chart_num = 3
        for index_type in ["NDVI", "NDMI"]:
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.suptitle(f"Performance Scalability vs. Data Size ({index_type})", fontsize=16)
            sizes = sorted([int(s) for s in time_results['scalability'][index_type].keys()])
            pixels = [s**2 for s in sizes]
            configs = list(time_results['scalability'][index_type][str(sizes[0])].keys())
            for config_label in configs:
                avg_times = [np.mean(time_results['scalability'][index_type][str(s)][config_label]) * 1000 for s in sizes]
                ax.plot(pixels, avg_times, marker='o', linestyle='-', label=config_label)
            ax.set_xlabel('Number of Pixels (Image Size)'); ax.set_ylabel('Average Time (ms)'); ax.set_xscale('log'); ax.set_yscale('log'); ax.legend(); ax.grid(True, which="both", ls="--")
            fig.savefig(os.path.join(self.CHARTS_DIR, f"{chart_num:02d}_size_scalability_{index_type.lower()}.png"), dpi=300)
            all_figures.append(fig); all_descriptions.append(f"This chart shows the 'break-even point' analysis for {index_type}. For small data sizes, the low-overhead single-thread CPU is fastest. As data size increases, the GPU's massive parallelism allows it to scale better. The point where the GPU line crosses the CPU line is the break-even point, beyond which the GPU becomes the superior choice.")
            chart_num += 1
            plt.close(fig)

        # Wykres 5: Narzut GPU
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        fig5.suptitle("GPU Overhead Analysis: First Run vs. Subsequent Runs", fontsize=16)
        gpu_times_raw = time_results['gpu_overhead']['NDVI']
        reps = np.arange(1, len(gpu_times_raw) + 1)
        bars = ax5.bar(reps, [t * 1000 for t in gpu_times_raw], color='#2ca02c')
        ax5.set_xlabel('Repetition Number'); ax5.set_ylabel('Execution Time (ms)'); ax5.set_xticks(reps); ax5.bar_label(bars, fmt='%.1f')
        fig5.savefig(os.path.join(self.CHARTS_DIR, "05_gpu_overhead.png"), dpi=300)
        all_figures.append(fig5); all_descriptions.append("This chart visualizes the 'warm-up' cost of the GPU. The first execution is significantly slower because the Just-In-Time (JIT) compiler (Taichi) needs to compile the Python code. Subsequent runs are much faster as they use the already compiled code, measuring mainly the data transfer and kernel execution time.")
        plt.close(fig5)

        # Wykres 6: Pamięć
        if memory_results:
            fig6, ax6 = plt.subplots(figsize=(10, 6))
            fig6.suptitle("Peak Memory Usage (RAM) per Method", fontsize=16)
            labels = list(memory_results.keys())
            mem_usages = list(memory_results.values())
            bars = ax6.bar(labels, mem_usages)
            ax6.set_ylabel('Peak Memory Usage (MiB)'); ax6.tick_params(axis='x', rotation=15); ax6.bar_label(bars, fmt='%.1f MiB')
            fig6.savefig(os.path.join(self.CHARTS_DIR, "06_memory_usage.png"), dpi=300)
            all_figures.append(fig6); all_descriptions.append("This chart shows the peak RAM usage of the main process. The GPU method offloads data to VRAM, consuming less RAM. The single-thread CPU is most RAM-efficient. The parallel CPU shows higher RAM usage due to the overhead of managing the process pool and shared memory segments.")
            plt.close(fig6)

        # Wykres 7: Przykładowa heatmapa
        sample_data_path = os.path.join(self.TEST_DATA_DIR, f"scaled_data_{self.STANDARD_TEST_SIZE}.tif")
        if os.path.exists(sample_data_path):
            bands_data = read_geotiff_bands(sample_data_path)
            ndvi_result, data_mask = calculate_index_cpu_single(bands_data, "NDVI")
            fig_heatmap = visualizer.create_heatmap_figure(
                ndvi_result, data_mask, "NDVI", f"Sample {self.STANDARD_TEST_SIZE}x{self.STANDARD_TEST_SIZE} Area"
            )
            fig_heatmap.savefig(os.path.join(self.CHARTS_DIR, "07_sample_output.png"), dpi=300)
            all_figures.append(fig_heatmap)
            all_descriptions.append("This chart shows a sample visual output of the NDVI calculation on a standard test dataset. It demonstrates the final product of the processing pipeline, visualizing vegetation density.")
            plt.close(fig_heatmap)

        return all_figures, all_descriptions