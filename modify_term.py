import tkinter as tk
from tkinter import ttk
import subprocess
import os
from tkinter import messagebox

class TerminalTab:
    def __init__(self, parent, app_reference, profile_name="Default", is_ssh=False, ssh_user=None, ssh_host=None):
        self.frame = ttk.Frame(parent)
        self.app_reference = app_reference
        self.profile_name = profile_name
        self.is_ssh = is_ssh
        self.ssh_user = ssh_user
        self.ssh_host = ssh_host
        self.terminal_process = None
        
        # Profile label
        self.profile_label = ttk.Label(self.frame, text=f"Profile: {profile_name}")
        self.profile_label.pack(anchor='w', padx=5, pady=2)
        
        # SSH connection details (only show if not an SSH tab)
        if not is_ssh:
            self.ssh_frame = ttk.Frame(self.frame)
            self.ssh_frame.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(self.ssh_frame, text="Host:").pack(side='left')
            self.host_entry = ttk.Entry(self.ssh_frame)
            self.host_entry.pack(side='left', padx=5)
            
            ttk.Label(self.ssh_frame, text="Username:").pack(side='left')
            self.user_entry = ttk.Entry(self.ssh_frame)
            self.user_entry.pack(side='left', padx=5)
            
            self.connect_btn = ttk.Button(self.ssh_frame, text="Connect SSH", command=self.connect_ssh)
            self.connect_btn.pack(side='left', padx=5)
        
        # Terminal frame
        self.terminal_frame = ttk.Frame(self.frame)
        self.terminal_frame.pack(fill='both', expand=True)
        
        # Start terminal (either local or SSH)
        if is_ssh:
            self.spawn_ssh_terminal()
        else:
            self.spawn_terminal()

    def cleanup(self):
        """Clean up terminal process when tab is closed"""
        if self.terminal_process:
            try:
                self.terminal_process.terminate()
                self.terminal_process.wait(timeout=1)  # Wait for process to terminate
            except subprocess.TimeoutExpired:
                self.terminal_process.kill()  # Force kill if it doesn't terminate
            except Exception as e:
                print(f"Error cleaning up process: {e}")
            finally:
                self.terminal_process = None

    def spawn_terminal(self):
        try:
            cwd = os.getcwd()
            self.terminal_process = subprocess.Popen([
                'xterm',
                '-into', '%d' % self.terminal_frame.winfo_id(),
                '-geometry', '80x24',
                '-title', f'Terminal - {self.profile_name}',
                '-fa', 'Monospace',
                '-fs', '10'
            ], cwd=cwd)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to spawn terminal: {str(e)}")

    def spawn_ssh_terminal(self):
        try:
            self.terminal_process = subprocess.Popen([
                'xterm',
                '-into', '%d' % self.terminal_frame.winfo_id(),
                '-geometry', '80x24',
                '-title', f'SSH: {self.ssh_user}@{self.ssh_host} - {self.profile_name}',
                '-fa', 'Monospace',
                '-fs', '10',
                '-e', f'ssh {self.ssh_user}@{self.ssh_host}'
            ])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect SSH: {str(e)}")

    def connect_ssh(self):
        host = self.host_entry.get()
        user = self.user_entry.get()
        
        if not host or not user:
            messagebox.showerror("Error", "Please provide both host and username")
            return
            
        self.app_reference.add_ssh_tab(user, host)

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Manager")
        
        # Configure style
        style = ttk.Style()
        style.configure('TNotebook', tabposition='nw')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Dictionary to store tab objects
        self.tabs = {}
        
        # Button frame
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        # Add tab button
        self.add_btn = ttk.Button(btn_frame, text="New Terminal", command=self.add_tab)
        self.add_btn.pack(side='left', padx=5)
        
        # Close current tab button
        self.close_btn = ttk.Button(btn_frame, text="Close Current Tab", command=self.close_current_tab)
        self.close_btn.pack(side='left', padx=5)
        
        # Profile name entry
        ttk.Label(btn_frame, text="Profile Name:").pack(side='left', padx=5)
        self.profile_entry = ttk.Entry(btn_frame)
        self.profile_entry.insert(0, "Default")
        self.profile_entry.pack(side='left', padx=5)
        
        # Add initial tab
        self.add_tab()
        
        # Bind double click to close tab
        self.notebook.bind('<Double-Button-1>', self.close_tab_event)
        
        # Bind right click to close tab
        self.notebook.bind('<Button-3>', self.close_tab_event)

    def close_tab_event(self, event):
        """Handle tab closing via mouse event"""
        clicked_tab = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
        if clicked_tab is not None:
            self.close_tab(clicked_tab)

    def close_current_tab(self):
        """Close the currently selected tab"""
        current = self.notebook.select()
        if current:
            tab_id = self.notebook.index(current)
            self.close_tab(tab_id)

    def close_tab(self, tab_id):
        """Close a specific tab"""
        if self.notebook.index('end') > 1:  # More than one tab
            try:
                # Get the terminal tab object
                for tab in self.tabs.values():
                    if tab.frame == self.notebook.select():
                        tab.cleanup()  # Clean up the terminal process
                        break
                
                # Remove the tab
                self.notebook.forget(tab_id)
                
                # Clean up the tabs dictionary
                self.tabs = {i: tab for i, tab in enumerate(self.tabs.values())}
            except Exception as e:
                print(f"Error closing tab: {e}")
        else:
            messagebox.showinfo("Info", "Cannot close the last tab")

    def add_tab(self):
        profile_name = self.profile_entry.get()
        tab_id = len(self.tabs)
        
        # Create the terminal tab
        terminal_tab = TerminalTab(self.notebook, self, profile_name)
        self.tabs[tab_id] = terminal_tab
        
        # Add to notebook with title
        self.notebook.add(terminal_tab.frame, text=f"Terminal - {profile_name}")
        
        # Switch to new tab
        self.notebook.select(terminal_tab.frame)

    def add_ssh_tab(self, user, host):
        profile_name = f"SSH - {user}@{host}"
        tab_id = len(self.tabs)
        
        # Create the terminal tab
        terminal_tab = TerminalTab(self.notebook, self, profile_name, is_ssh=True, ssh_user=user, ssh_host=host)
        self.tabs[tab_id] = terminal_tab
        
        # Add to notebook with title
        self.notebook.add(terminal_tab.frame, text=profile_name)
        
        # Switch to new tab
        self.notebook.select(terminal_tab.frame)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = TerminalApp(root)
    root.mainloop()