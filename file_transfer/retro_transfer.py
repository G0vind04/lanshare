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
        self.peers = {}
        self.server_running = False

        # Peer Discovery
        self.peer_discovery = PeerDiscovery()
        self.peer_discovery.register_service("MyDevice", 12345)
        self.peer_discovery.discover_peers()

        # GUI Components
        self.create_widgets()

        # Start server in a separate thread
        self.start_server_thread()

    def create_widgets(self):
        # Peer List
        self.peer_list_label = tk.Label(self.root, text="Discovered Peers:")
        self.peer_list_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.peer_listbox = tk.Listbox(self.root, height=5)
        self.peer_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.refresh_button = tk.Button(self.root, text="Refresh Peers", command=self.refresh_peers)
        self.refresh_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Send File Section
        self.send_file_label = tk.Label(self.root, text="Send File:")
        self.send_file_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(self.root, textvariable=self.file_path_var, width=40)
        self.file_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_file_gui)
        self.send_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky="ew")

    def refresh_peers(self):
        self.peer_listbox.delete(0, tk.END)
        self.peers = self.peer_discovery.peers
        for name, info in self.peers.items():
            self.peer_listbox.insert(tk.END, f"{name} ({info['address']}:{info['port']})")

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)

    def send_file_gui(self):
        selected_peer_index = self.peer_listbox.curselection()
        if not selected_peer_index:
            messagebox.showerror("Error", "Please select a peer.")
            return

        selected_peer_name = self.peer_listbox.get(selected_peer_index)
        peer_info = self.peers[selected_peer_name.split(" ")[0]]
        ip = peer_info["address"]
        port = peer_info["port"]
        file_path = self.file_path_var.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return

        # Run file sending in a separate thread
        Thread(target=send_file, args=(ip, port, file_path)).start()
        self.status_var.set(f"Sending file to {selected_peer_name}...")

    def start_server_thread(self):
        if not self.server_running:
            Thread(target=start_server, args=(12345,), daemon=True).start()
            self.server_running = True
            self.status_var.set("Server is running and waiting for incoming files...")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()