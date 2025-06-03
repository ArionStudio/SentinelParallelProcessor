import tkinter as tk
from src.gui.app import MainApplication

def main():
    # Create root window
    root = tk.Tk()
    
    # Create and run application
    app = MainApplication(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
