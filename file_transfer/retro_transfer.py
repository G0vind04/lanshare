import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from peer_discovery import PeerDiscovery
from file_transfer_client import send_file
from file_transfer_server import start_server

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer App")
        self.root.geometry("600x500")
        self.root.configure(padx=20, pady=20)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Section.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Status.TLabel", font=("Helvetica", 10, "italic"))
        
        self.peers = {}
        self.server_running = False

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

    def create_widgets(self):
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="File Transfer Application", 
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

        refresh_button = ttk.Button(
            peer_frame, 
            text="Refresh Peers", 
            command=self.refresh_peers
        )
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

        add_peer_button = ttk.Button(
            input_frame, 
            text="Add Peer", 
            command=self.add_peer_manually
        )
        add_peer_button.pack(side=tk.LEFT)

        # File Transfer Section
        file_selection_frame = ttk.Frame(file_frame)
        file_selection_frame.pack(fill=tk.X, pady=5)

        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_selection_frame, textvariable=self.file_path_var)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_button = ttk.Button(
            file_selection_frame, 
            text="Browse", 
            command=self.browse_file
        )
        browse_button.pack(side=tk.LEFT, padx=(0, 10))

        send_button = ttk.Button(
            file_selection_frame, 
            text="Send File", 
            command=self.send_file_gui
        )
        send_button.pack(side=tk.LEFT)

        # Status Bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            style="Status.TLabel"
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def refresh_peers(self):
        self.peer_listbox.delete(*self.peer_listbox.get_children())
        self.peers = self.peer_discovery.peers
        for name, info in self.peers.items():
            self.peer_listbox.insert(
                "", 
                "end", 
                values=(name, f"{info['address']}:{info['port']}")
            )

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)

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

        Thread(target=send_file, args=(
            peer_info["address"], 
            peer_info["port"], 
            file_path
        )).start()
        
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
        self.status_var.set(f"Added peer {peer_name} manually.")

    def start_server_thread(self):
        if not self.server_running:
            Thread(target=start_server, args=(12345,), daemon=True).start()
            self.server_running = True
            self.status_var.set("Server is running and waiting for incoming files...")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()