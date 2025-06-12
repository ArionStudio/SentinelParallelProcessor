# main.py

import matplotlib
matplotlib.use("TkAgg")

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
    freeze_support()
    main()