import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tkterm.tkterm import Terminal

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TkTerm with Resizable Side Panel")
        self.geometry("1000x600")

        # Create main paned window
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Create and add side panel
        self.side_panel = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.side_panel, weight=1)

        # Add some widgets to the side panel (customize as needed)
        ttk.Label(self.side_panel, text="Side Panel").pack(pady=10)
        ttk.Button(self.side_panel, text="Run Command 1", command=lambda: self.run_command("echo Hello from Button 1")).pack(pady=5)
        ttk.Button(self.side_panel, text="Run Command 2", command=lambda: self.run_command("echo Hello from Button 2")).pack(pady=5)

        # Create and add TkTerm
        self.terminal_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.terminal_frame, weight=3)
        
        self.terminal = Terminal(self.terminal_frame)
        self.terminal.pack(fill=tk.BOTH, expand=True)

    def run_command(self, command):
        self.terminal.run_command(command)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()