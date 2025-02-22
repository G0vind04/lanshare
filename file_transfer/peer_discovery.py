from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import socket
import threading

class PeerDiscovery:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.peers = {}

    def register_service(self, name, port):
        info = ServiceInfo(
            "_filetransfer._tcp.local.",
            f"{name}._filetransfer._tcp.local.",
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=port,
            properties={},
        )
        self.zeroconf.register_service(info)

    def discover_peers(self):
        """Start the service browser in a separate thread."""
        class MyListener:
            def __init__(self, peers):
                self.peers = peers

            def add_service(self, zeroconf, type, name):
                info = zeroconf.get_service_info(type, name)
                if info:
                    self.peers[name] = {
                        "address": socket.inet_ntoa(info.addresses[0]),
                        "port": info.port,
                    }
                    print(f"Discovered peer: {name} at {self.peers[name]['address']}:{self.peers[name]['port']}")

            def remove_service(self, zeroconf, type, name):
                """Optionally handle service removal."""
                if name in self.peers:
                    del self.peers[name]
                    print(f"Peer {name} has been removed.")

        # Create the listener
        listener = MyListener(self.peers)

        # Start service discovery on a separate thread
        def run_browser():
            browser = ServiceBrowser(self.zeroconf, "_filetransfer._tcp.local.", listener)
            try:
                while True:
                    pass  # Keep the browser running
            except KeyboardInterrupt:
                pass

        # Start the discovery process in a separate thread to not block the main thread
        discovery_thread = threading.Thread(target=run_browser, daemon=True)
        discovery_thread.start()

    def close(self):
        self.zeroconf.close()
