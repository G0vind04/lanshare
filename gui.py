import sys
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal,QThreadPool
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem, QGroupBox, QFileDialog, QMessageBox

from peer_discovery import PeerDiscovery
from file_transfer_client import send_file
from file_transfer_server import start_server
import pyperclip

class FileTransferApp(QWidget):
    status_update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Transfer App")
        self.setGeometry(100, 100, 600, 600)

        self.peers = {}
        self.server_running = False
        self.status_queue = []

        self.peer_discovery = PeerDiscovery()
        self.peer_discovery.register_service("MyDevice", 12345)
        self.peer_discovery.discover_peers()

        self.init_ui()
        self.start_server_thread()
        self.status_update_signal.connect(self.add_transfer_log)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("File Transfer Application")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Peer Management Section
        peer_group = QGroupBox("Peer Management")
        peer_layout = QVBoxLayout(peer_group)
        self.peer_listview = QTreeWidget()
        self.peer_listview.setColumnCount(2)
        self.peer_listview.setHeaderLabels(["Peer Name", "Address"])
        peer_layout.addWidget(self.peer_listview)
        refresh_button = QPushButton("Refresh Peers")
        refresh_button.clicked.connect(self.refresh_peers)
        peer_layout.addWidget(refresh_button)
        main_layout.addWidget(peer_group)

        # Manual Peer Addition Section
        manual_peer_group = QGroupBox("Manual Peer Addition")
        manual_peer_layout = QHBoxLayout(manual_peer_group)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Address")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        add_peer_button = QPushButton("Add Peer")
        add_peer_button.clicked.connect(self.add_peer_manually)
        manual_peer_layout.addWidget(self.ip_input)
        manual_peer_layout.addWidget(self.port_input)
        manual_peer_layout.addWidget(add_peer_button)
        main_layout.addWidget(manual_peer_group)

        # File Transfer Section
        file_group = QGroupBox("File Transfer")
        file_layout = QHBoxLayout(file_group)
        self.file_path_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        send_button = QPushButton("Send File")
        send_button.clicked.connect(self.send_file_gui)
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(browse_button)
        file_layout.addWidget(send_button)
        main_layout.addWidget(file_group)

        # Clipboard Text Transfer Section
        clipboard_group = QGroupBox("Clipboard Text Transfer")
        clipboard_layout = QVBoxLayout(clipboard_group)
        self.clipboard_text = QTextEdit()
        clipboard_send_button = QPushButton("Send Clipboard Text")
        clipboard_send_button.clicked.connect(self.send_clipboard_text)
        clipboard_clear_button = QPushButton("Clear Text")
        clipboard_clear_button.clicked.connect(self.clear_clipboard_text)
        clipboard_layout.addWidget(self.clipboard_text)
        clipboard_layout.addWidget(clipboard_send_button)
        clipboard_layout.addWidget(clipboard_clear_button)
        main_layout.addWidget(clipboard_group)

        # Transfer Status Log Section
        transfer_group = QGroupBox("Transfer Status")
        self.transfer_log = QTextEdit()
        self.transfer_log.setReadOnly(True)
        transfer_layout = QVBoxLayout(transfer_group)
        transfer_layout.addWidget(self.transfer_log)
        main_layout.addWidget(transfer_group)

        # Status Bar
        self.status_label = QLabel("Status")
        main_layout.addWidget(self.status_label)

    def clear_clipboard_text(self):
        self.clipboard_text.clear()

    def send_clipboard_text(self):
        selected_item = self.peer_listview.selectedItems()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a peer.")
            return
        peer_name = selected_item[0].text(0)
        peer_info = self.peers[peer_name]

        clipboard_content = self.clipboard_text.toPlainText().strip()
        if not clipboard_content:
            QMessageBox.warning(self, "Error", "Clipboard content is empty.")
            return

        def send_with_status():
            try:
                self.add_transfer_log(f"Starting clipboard text transfer to {peer_name}")
                send_file(peer_info["address"], peer_info["port"], clipboard_content)
                self.add_transfer_log(f"Clipboard text transfer completed successfully to {peer_name}")
            except Exception as e:
                self.add_transfer_log(f"Error during clipboard text transfer: {str(e)}")

        QThreadPool.globalInstance().start(send_with_status)
        self.status_label.setText(f"Sending clipboard text to {peer_name}...")

    def update_clipboard_text(self, text):
        """Update the clipboard text box with received text"""
        self.clipboard_text.setPlainText(text)

    def add_transfer_log(self, message):
        """Add a message to the transfer log with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.transfer_log.append(f"[{timestamp}] {message}")

    def refresh_peers(self):
        self.peer_listview.clear()
        self.peers = self.peer_discovery.peers
        for name, info in self.peers.items():
            item = QTreeWidgetItem(self.peer_listview)
            item.setText(0, name)
            item.setText(1, f"{info['address']}:{info['port']}")
        self.add_transfer_log("Peer list refreshed")

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File")
        if file_path:
            self.file_path_input.setText(file_path)
            self.add_transfer_log(f"Selected file: {file_path}")

    def send_file_gui(self):
        selected_item = self.peer_listview.selectedItems()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a peer.")
            return
        peer_name = selected_item[0].text(0)
        peer_info = self.peers[peer_name]

        file_path = self.file_path_input.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a file.")
            return

        def send_with_status():
            try:
                self.add_transfer_log(f"Starting file transfer to {peer_name}")
                send_file(peer_info["address"], peer_info["port"], file_path)
                self.add_transfer_log(f"File transfer completed successfully to {peer_name}")
            except Exception as e:
                self.add_transfer_log(f"Error during file transfer: {str(e)}")

        QThreadPool.globalInstance().start(send_with_status)
        self.status_label.setText(f"Sending file to {peer_name}...")

    def add_peer_manually(self):
        ip = self.ip_input.text()
        port = self.port_input.text()
        if not ip or not port:
            QMessageBox.warning(self, "Error", "Please enter both IP and port.")
            return
        try:
            port = int(port)
        except ValueError:
            QMessageBox.warning(self, "Error", "Port must be a number.")
            return
        peer_name = f"ManualPeer-{ip}:{port}"
        self.peers[peer_name] = {"address": ip, "port": port}

        item = QTreeWidgetItem(self.peer_listview)
        item.setText(0, peer_name)
        item.setText(1, f"{ip}:{port}")
        self.ip_input.clear()
        self.port_input.clear()
        self.add_transfer_log(f"Added new peer manually: {peer_name}")
        self.status_label.setText(f"Added peer {peer_name} manually.")

    def start_server_thread(self):
        if not self.server_running:
            def run_server_with_status():
                def status_callback(message):
                    self.add_transfer_log(message)

                start_server(12345, status_callback)

            QThreadPool.globalInstance().start(run_server_with_status)
            self.server_running = True
            self.add_transfer_log("Server started and waiting for incoming files...")
            self.status_label.setText("Server is running and waiting for incoming files...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTransferApp()
    window.show()
    sys.exit(app.exec_())
