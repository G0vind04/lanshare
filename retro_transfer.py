import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import os
from tkinterdnd2 import DND_FILES, TkinterDnD
from file_transfer_server import start_server
from file_transfer_client import send_file
from peer_discovery import PeerDiscovery


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
        # Configure modern styles for widgets
        style = ttk.Style()
        style.configure("Header.TFrame", background="white")
        style.configure("DropZone.TFrame", background="white")
        style.configure("Toggle.TCheckbutton", background="white")

        # Custom toggle switch style
        style.layout("Toggle.TCheckbutton",
                     [('Checkbutton.padding',
                       {'children': [('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
                                     ('Checkbutton.label', {'side': 'right', 'sticky': ''})],
                        'sticky': 'nswe'})])

        # Progress bar style
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor="#E0E0E0",
                        background="#4CAF50",
                        thickness=5)

    def create_layout(self):
        # Header
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=10)

        # Title and toggle switch
        title_frame = ttk.Frame(header_frame, style="Header.TFrame")
        title_frame.pack(side=tk.LEFT)

        tk.Label(title_frame,
                 text="P2P File Sharing",
                 font=("Segoe UI", 18, "bold"),
                 bg="white").pack(side=tk.LEFT, padx=(0, 20))

        # Custom toggle switch
        self.create_toggle_switch(title_frame)

        # Add Peer button
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

        # Drop zone
        self.create_drop_zone()

        # Progress bar
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

        # Draw toggle switch
        self.draw_toggle_switch()

        # Bind click event
        self.switch_canvas.bind("<Button-1>", self.toggle_receiving)

        tk.Label(switch_frame,
                 text="Receiving",
                 font=("Segoe UI", 10),
                 bg="white").pack(side=tk.LEFT, padx=(10, 0))

    def draw_toggle_switch(self):
        self.switch_canvas.delete("all")

        # Draw background
        if self.is_receiving.get():
            bg_color = "#4CAF50"  # Green when on
        else:
            bg_color = "#E0E0E0"  # Gray when off

        self.switch_canvas.create_rounded_rectangle(0, 0, 50, 24,
                                                    radius=12,
                                                    fill=bg_color)

        # Draw toggle
        toggle_x = 30 if self.is_receiving.get() else 6
        self.switch_canvas.create_oval(toggle_x, 2,
                                       toggle_x + 20, 22,
                                       fill="white")

    def create_drop_zone(self):
        self.drop_frame = ttk.Frame(self.root, style="DropZone.TFrame")
        self.drop_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create dashed border
        self.drop_canvas = tk.Canvas(self.drop_frame,
                                     bg="white",
                                     highlightthickness=1,
                                     highlightbackground="#E0E0E0")
        self.drop_canvas.pack(fill=tk.BOTH, expand=True)

        # Draw dashed border
        self.draw_dashed_border()

        # Drop zone text
        self.drop_canvas.create_text(400, 300,
                                     text="Drag and drop files here, or click to select files",
                                     font=("Segoe UI", 14),
                                     fill="#666666")

        # Bind events
        self.drop_canvas.bind("<Button-1>", self.select_files)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def draw_dashed_border(self):
        # Draw dashed rectangle
        dash_pattern = [10, 10]  # 10 pixels on, 10 pixels off
        self.drop_canvas.create_rectangle(10, 10,
                                          self.drop_canvas.winfo_width() - 10,
                                          self.drop_canvas.winfo_height() - 10,
                                          outline="#E0E0E0",
                                          dash=dash_pattern)

    def toggle_receiving(self, event=None):
        self.is_receiving.set(not self.is_receiving.get())
        self.draw_toggle_switch()

    def add_peer(self):
        # Open a dialog to add a new peer
        name = simpledialog.askstring("Add Peer", "Enter peer name:")
        ip = simpledialog.askstring("Add Peer", "Enter peer IP address:")
        port = simpledialog.askinteger("Add Peer", "Enter peer port:", minvalue=1, maxvalue=65535)

        if name and ip and port:
            self.peers[name] = {"address": ip, "port": port}
            messagebox.showinfo("Success", f"Added peer: {name} ({ip}:{port})")
            self.refresh_peers()

    def refresh_peers(self):
        # Refresh the list of peers (if needed)
        pass  # Placeholder for future implementation

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
                # Start file transfer for each file
                threading.Thread(target=self.transfer_file,
                                  args=({"address": "peer_address"}, file),
                                  daemon=True).start()

    def transfer_file(self, peer_info, file_path):
        try:
            total_size = os.path.getsize(file_path)
            sent_size = 0

            def update_progress(chunk_size):
                nonlocal sent_size
                sent_size += chunk_size
                progress = (sent_size / total_size) * 100
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
        server_thread = threading.Thread(target=start_server,
                                         args=(12345,
                                               self.received_files_path.get(),
                                               self.handle_received_file),
                                         daemon=True)
        server_thread.start()

    def handle_received_file(self, file_name):
        # Implement received file handling here
        pass


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
    root = TkinterDnD.Tk()  # Use TkinterDnD instead of regular Tk
    app = ModernFileTransferGUI(root)
    root.mainloop()