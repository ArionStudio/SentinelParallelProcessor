# main.py

import matplotlib
# ZMIANA: Ustawienie backendu Matplotlib PRZED importem pyplot
# To kluczowe dla stabilności w aplikacjach GUI z wątkami.
matplotlib.use("Agg")

import tkinter as tk
from src.gui.app import MainApplication
from multiprocessing import freeze_support

def main():
    # Create root window
    root = tk.Tk()
    
    # Create and run application
    app = MainApplication(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    # freeze_support() jest potrzebne dla skompilowanych aplikacji (np. PyInstaller)
    # na Windows i macOS.
    freeze_support()
    main()