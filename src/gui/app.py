import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.gui.views.login_view import LoginView

class MainApplication(ttk.Frame):
    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self.root = root
        self.root.title("Sentinel Hub Processor")
        
        # Configure main window
        self.root.geometry("800x600")  # Set initial size
        self._center_window()
        
        # Configure main frame
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main frame for views
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Show login view
        self.show_login_view()

    def _center_window(self):
        """Center the main window on the screen"""
        # Update the window to ensure we have the correct dimensions
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position
        self.root.geometry(f"+{x}+{y}")

    def show_login_view(self):
        """Show the login view"""
        self.login_view = LoginView(
            self.main_frame,
            on_login_success=self.on_login_success
        )
        self.login_view.grid(row=0, column=0, sticky="nsew")

    def on_login_success(self):
        """Handle successful login"""
        # TODO: Show main application view
        pass

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApplication()
    app.run() 