import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from peer_discovery import PeerDiscovery
from file_transfer_client import send_file
from file_transfer_server import start_server
import queue
import time
import pyperclip  # Add pyperclip for clipboard operations

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LanSher")
        self.root.geometry("600x600")  # Increased height for transfer logs
        self.root.configure(padx=20, pady=20)

        self.set_app_icon()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Courier Prime", 20, "bold"))
        self.style.configure("Section.TLabel", font=("Courier Prime", 12, "bold"))
        self.style.configure("Status.TLabel", font=("Courier Prime", 10, "italic"))
        
        self.peers = {}
        self.server_running = False
        
        
        # Queue for handling status updates
        self.status_queue = queue.Queue()
        # Peer Discovery
        self.peer_discovery = PeerDiscovery()
        self.peer_discovery.register_service("MyDevice", 12345)
        self.peer_discovery.discover_peers()
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # Create all widgets
        self.create_widgets()
        # Start server in a separate thread
        self.start_server_thread()
        
        # Start the status update checker
        self.check_status_updates()
    
    def set_app_icon(self):
        """Set the app icon from the given file path."""
        try:
            icon = tk.PhotoImage(file=r"assets\lion.png")
            self.root.iconphoto(False, icon)
        except Exception as e:
            messagebox.showwarning("Icon Loading Error", f"Unable to load icon: {e}")


    def create_widgets(self):
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="LanSher", 
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        # Create frames for different sections
        peer_frame = ttk.LabelFrame(self.main_frame, text="Peer Management", padding=10)
        peer_frame.pack(fill=tk.X, pady=(0, 15))
        manual_frame = ttk.LabelFrame(self.main_frame, text="Manual Peer Addition", padding=10)
        manual_frame.pack(fill=tk.X, pady=(0, 15))
        file_frame = ttk.LabelFrame(self.main_frame, text="File Transfer", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Clipboard Text Section (updated with clear button)
        clipboard_frame = ttk.LabelFrame(self.main_frame, text="Clipboard Text Transfer", padding=10)
        clipboard_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.clipboard_text = tk.Text(clipboard_frame, height=4, wrap=tk.WORD)
        self.clipboard_text.pack(fill=tk.BOTH, expand=True)
        
        clipboard_buttons_frame = ttk.Frame(clipboard_frame)
        clipboard_buttons_frame.pack(fill=tk.X, pady=5)
        
        clipboard_send_button = ttk.Button(clipboard_buttons_frame, text="Send Clipboard Text", command=self.send_clipboard_text)
        clipboard_send_button.pack(side=tk.LEFT, padx=5)
        
        clipboard_clear_button = ttk.Button(clipboard_buttons_frame, text="Clear Text", command=self.clear_clipboard_text)
        clipboard_clear_button.pack(side=tk.LEFT, padx=5)
        
        # Transfer Log Section
        transfer_frame = ttk.LabelFrame(self.main_frame, text="Transfer Status", padding=10)
        transfer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Add transfer log text widget
        self.transfer_log = tk.Text(transfer_frame, height=8, wrap=tk.WORD)
        self.transfer_log.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar to transfer log
        scrollbar = ttk.Scrollbar(transfer_frame, orient="vertical", command=self.transfer_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transfer_log.configure(yscrollcommand=scrollbar.set)
        
        # Peer List Section
        self.peer_listbox = ttk.Treeview(
            peer_frame, 
            columns=("name", "address"), 
            show="headings", 
            height=5
        )
        self.peer_listbox.heading("name", text="Peer Name")
        self.peer_listbox.heading("address", text="Address")
        self.peer_listbox.pack(fill=tk.X, pady=(0, 10))
        
        refresh_button = ttk.Button(peer_frame, text="Refresh Peers", command=self.refresh_peers)
        refresh_button.pack(fill=tk.X)
        
        # Manual Peer Addition Section
        input_frame = ttk.Frame(manual_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="IP Address:").pack(side=tk.LEFT, padx=(0, 10))
        self.ip_var = tk.StringVar()
        ip_entry = ttk.Entry(input_frame, textvariable=self.ip_var, width=20)
        ip_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(input_frame, text="Port:").pack(side=tk.LEFT, padx=(0, 10))
        self.port_var = tk.StringVar()
        port_entry = ttk.Entry(input_frame, textvariable=self.port_var, width=10)
        port_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        add_peer_button = ttk.Button(input_frame, text="Add Peer", command=self.add_peer_manually)
        add_peer_button.pack(side=tk.LEFT)
        
        # File Transfer Section
        file_selection_frame = ttk.Frame(file_frame)
        file_selection_frame.pack(fill=tk.X, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_selection_frame, textvariable=self.file_path_var)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_button = ttk.Button(file_selection_frame, text="Browse", command=self.browse_file)
        browse_button.pack(side=tk.LEFT, padx=(0, 10))
        
        send_button = ttk.Button(file_selection_frame, text="Send File", command=self.send_file_gui)
        send_button.pack(side=tk.LEFT)
        
        # Status Bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, style="Status.TLabel")
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def clear_clipboard_text(self):
        """Clear the clipboard text box"""
        self.clipboard_text.delete(1.0, tk.END)

    def send_clipboard_text(self):
        selected_item = self.peer_listbox.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a peer.")
            return
        peer_values = self.peer_listbox.item(selected_item)['values']
        peer_name = peer_values[0]
        peer_info = self.peers[peer_name]
        
        clipboard_content = self.clipboard_text.get("1.0", "end-1c").strip()
        if not clipboard_content:
            messagebox.showerror("Error", "Clipboard content is empty.")
            return
        
        def send_with_status():
            try:
                self.add_transfer_log(f"Starting clipboard text transfer to {peer_name}")
                # Send clipboard content to peer (can be a different send function)
                send_file(peer_info["address"], peer_info["port"], clipboard_content)
                self.add_transfer_log(f"Clipboard text transfer completed successfully to {peer_name}")
            except Exception as e:
                self.add_transfer_log(f"Error during clipboard text transfer: {str(e)}")
                
        Thread(target=send_with_status).start()
        self.status_var.set(f"Sending clipboard text to {peer_name}...")

    def update_clipboard_text(self, text):
        """Update the clipboard text box with received text"""
        self.clipboard_text.delete(1.0, tk.END)
        self.clipboard_text.insert(tk.END, text)

    def add_transfer_log(self, message):
        """Add a message to the transfer log with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.status_queue.put(f"[{timestamp}] {message}\n")
        
        # Check if the message contains received text and update clipboard box
        if "[RECEIVED] Text message: " in message:
            received_text = message.split("[RECEIVED] Text message: ")[1]
            self.root.after(0, lambda: self.update_clipboard_text(received_text))

    def check_status_updates(self):
        """Check for status updates in the queue and update the GUI"""
        try:
            while True:
                message = self.status_queue.get_nowait()
                self.transfer_log.insert(tk.END, message)
                self.transfer_log.see(tk.END)  # Auto-scroll to the bottom
        except queue.Empty:
            pass
        finally:
            # Schedule the next check
            self.root.after(100, self.check_status_updates)

    def refresh_peers(self):
        self.peer_listbox.delete(*self.peer_listbox.get_children())
        self.peers = self.peer_discovery.peers
        for name, info in self.peers.items():
            self.peer_listbox.insert(
                "", 
                "end", 
                values=(name, f"{info['address']}:{info['port']}")
            )
        self.add_transfer_log("Peer list refreshed")

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)
            self.add_transfer_log(f"Selected file: {file_path}")

    def send_file_gui(self):
        selected_item = self.peer_listbox.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a peer.")
            return
        peer_values = self.peer_listbox.item(selected_item)['values']
        peer_name = peer_values[0]
        peer_info = self.peers[peer_name]
        
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return
        
        def send_with_status():
            try:
                self.add_transfer_log(f"Starting file transfer to {peer_name}")
                send_file(peer_info["address"], peer_info["port"], file_path)
                self.add_transfer_log(f"File transfer completed successfully to {peer_name}")
            except Exception as e:
                self.add_transfer_log(f"Error during file transfer: {str(e)}")
                
        Thread(target=send_with_status).start()
        self.status_var.set(f"Sending file to {peer_name}...")

    def add_peer_manually(self):
        ip = self.ip_var.get()
        port = self.port_var.get()
        if not ip or not port:
            messagebox.showerror("Error", "Please enter both IP and port.")
            return
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.")
            return
        peer_name = f"ManualPeer-{ip}:{port}"
        self.peers[peer_name] = {"address": ip, "port": port}
        
        self.peer_listbox.insert(
            "", 
            "end", 
            values=(peer_name, f"{ip}:{port}")
        )
        self.ip_var.set("")
        self.port_var.set("")
        self.add_transfer_log(f"Added new peer manually: {peer_name}")
        self.status_var.set(f"Added peer {peer_name} manually.")
        
    def start_server_thread(self):
        if not self.server_running:
            def run_server_with_status():
                def status_callback(message):
                    self.add_transfer_log(message)
                
                start_server(12345, status_callback)
            Thread(target=run_server_with_status, daemon=True).start()
            self.server_running = True
            self.add_transfer_log("Server started and waiting for incoming files...")
            self.status_var.set("Server is running and waiting for incoming files...")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()