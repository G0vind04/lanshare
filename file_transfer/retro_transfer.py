import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import os
from tkinterdnd2 import DND_FILES, TkinterDnD
from zeroconf import ServiceBrowser, Zeroconf

# PeerDiscovery class
class PeerDiscovery:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.peers = {}

    def register_service(self, name, port):
        # Placeholder for service registration
        # You'll need to implement this method based on your requirements
        pass

    def discover_peers(self):
        class MyListener:
            def __init__(self, outer):
                self.outer = outer

            def add_service(self, zeroconf, type, name):
                info = zeroconf.get_service_info(type, name)
                if info:
                    self.outer.peers[name] = {
                        "address": info.parsed_addresses()[0],
                        "port": info.port
                    }
                    print(f"Discovered peer: {name} at {info.parsed_addresses()[0]}:{info.port}")

            def remove_service(self, zeroconf, type, name):
                if name in self.outer.peers:
                    del self.outer.peers[name]
                    print(f"Peer removed: {name}")

            def update_service(self, zeroconf, type, name):
                # This method is now provided to avoid the warning
                pass

        browser = ServiceBrowser(self.zeroconf, "_filetransfer._tcp.local.", MyListener(self))

    def __del__(self):
        self.zeroconf.close()

# File transfer server and client functions (placeholders)
def start_server(port, save_path, file_received_callback):
    # Placeholder for server implementation
    print(f"Server started on port {port}, saving files to {save_path}")

def send_file(address, port, file_path, progress_callback=None):
    # Placeholder for file sending implementation
    print(f"Sending file {file_path} to {address}:{port}")
    # Simulate progress
    for i in range(0, 101, 10):
        if progress_callback:
            progress_callback(i)
        import time
        time.sleep(0.5)

# Main GUI class
class ModernFileTransferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P File Sharing")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        self.peers = {}
        self.is_receiving = tk.BooleanVar(value=False)
        self.received_files_path = tk.StringVar(value=os.path.expanduser("~"))

        self.discovery = PeerDiscovery()
        self.discovery.register_service("MyDevice", 12345)
        self.discovery.discover_peers()

        self.setup_styles()
        self.create_layout()
        self.start_server_thread()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Header.TFrame", background="white")
        style.configure("DropZone.TFrame", background="white")
        style.configure("Toggle.TCheckbutton", background="white")
        style.layout("Toggle.TCheckbutton",
                     [('Checkbutton.padding',
                       {'children': [('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
                                     ('Checkbutton.label', {'side': 'right', 'sticky': ''})],
                        'sticky': 'nswe'})])
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor="#E0E0E0",
                        background="#4CAF50",
                        thickness=5)

    def create_layout(self):
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=10)

        title_frame = ttk.Frame(header_frame, style="Header.TFrame")
        title_frame.pack(side=tk.LEFT)

        tk.Label(title_frame,
                 text="P2P File Sharing",
                 font=("Segoe UI", 18, "bold"),
                 bg="white").pack(side=tk.LEFT, padx=(0, 20))

        self.create_toggle_switch(title_frame)

        add_peer_btn = tk.Button(header_frame,
                                 text="+ Add Peer",
                                 font=("Segoe UI", 10),
                                 bg="black",
                                 fg="white",
                                 bd=0,
                                 padx=15,
                                 pady=8,
                                 command=self.add_peer)
        add_peer_btn.pack(side=tk.RIGHT)

        self.create_drop_zone()

        self.progress = ttk.Progressbar(self.root,
                                        orient="horizontal",
                                        length=760,
                                        mode="determinate",
                                        style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10)

    def create_toggle_switch(self, parent):
        switch_frame = ttk.Frame(parent, style="Header.TFrame")
        switch_frame.pack(side=tk.LEFT)

        self.switch_canvas = tk.Canvas(switch_frame,
                                       width=50,
                                       height=24,
                                       bg="white",
                                       highlightthickness=0)
        self.switch_canvas.pack(side=tk.LEFT)

        self.draw_toggle_switch()
        self.switch_canvas.bind("<Button-1>", self.toggle_receiving)

        tk.Label(switch_frame,
                 text="Receiving",
                 font=("Segoe UI", 10),
                 bg="white").pack(side=tk.LEFT, padx=(10, 0))

    def draw_toggle_switch(self):
        self.switch_canvas.delete("all")
        bg_color = "#4CAF50" if self.is_receiving.get() else "#E0E0E0"
        self.switch_canvas.create_rounded_rectangle(0, 0, 50, 24,
                                                    radius=12,
                                                    fill=bg_color)
        toggle_x = 30 if self.is_receiving.get() else 6
        self.switch_canvas.create_oval(toggle_x, 2,
                                       toggle_x + 20, 22,
                                       fill="white")

    def create_drop_zone(self):
        self.drop_frame = ttk.Frame(self.root, style="DropZone.TFrame")
        self.drop_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.drop_canvas = tk.Canvas(self.drop_frame,
                                     bg="white",
                                     highlightthickness=1,
                                     highlightbackground="#E0E0E0")
        self.drop_canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_dashed_border()

        self.drop_canvas.create_text(400, 300,
                                     text="Drag and drop files here, or click to select files",
                                     font=("Segoe UI", 14),
                                     fill="#666666")

        self.drop_canvas.bind("<Button-1>", self.select_files)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def draw_dashed_border(self):
        dash_pattern = [10, 10]
        self.drop_canvas.create_rectangle(10, 10,
                                          self.drop_canvas.winfo_width() - 10,
                                          self.drop_canvas.winfo_height() - 10,
                                          outline="#E0E0E0",
                                          dash=dash_pattern)

    def toggle_receiving(self, event=None):
        self.is_receiving.set(not self.is_receiving.get())
        self.draw_toggle_switch()

    def add_peer(self):
        name = simpledialog.askstring("Add Peer", "Enter peer name:")
        ip = simpledialog.askstring("Add Peer", "Enter peer IP address:")
        port = simpledialog.askinteger("Add Peer", "Enter peer port:", minvalue=1, maxvalue=65535)

        if name and ip and port:
            self.peers[name] = {"address": ip, "port": port}
            messagebox.showinfo("Success", f"Added peer: {name} ({ip}:{port})")
            self.refresh_peers()

    def refresh_peers(self):
        # Placeholder for refreshing the list of peers
        pass

    def select_files(self, event=None):
        files = filedialog.askopenfilenames()
        if files:
            self.handle_files(files)

    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self.handle_files(files)

    def handle_files(self, files):
        if not self.is_receiving.get():
            for file in files:
                threading.Thread(target=self.transfer_file,
                                  args=({"address": "peer_address"}, file),
                                  daemon=True).start()

    def transfer_file(self, peer_info, file_path):
        try:
            total_size = os.path.getsize(file_path)
            sent_size = 0

            def update_progress(progress):
                self.root.after(0, lambda: self.progress.config(value=progress))

            send_file(peer_info["address"], 12345, file_path, progress_callback=update_progress)
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Sent {os.path.basename(file_path)}",
                icon="info"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Failed to send file: {str(e)}",
                icon="error"))

    def start_server_thread(self):
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()

    def run_server(self):
        start_server(12345, self.received_files_path.get(), self.handle_received_file)

    def handle_received_file(self, file_name):
        self.root.after(0, lambda: messagebox.showinfo(
            "File Received",
            f"Received file: {file_name}",
            icon="info"))

# Helper method to create rounded rectangles
def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1]
    return self.create_polygon(points, **kwargs, smooth=True)

# Add the rounded rectangle method to Canvas
tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ModernFileTransferGUI(root)
    root.mainloop()