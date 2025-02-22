from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import socket
import threading
import time

class PeerDiscovery:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.peers = {}
        self.running = False

    def register_service(self, name, port):
        """Register this device as a discoverable service."""
        try:
            info = ServiceInfo(
                "_filetransfer._tcp.local.",
                f"{name}._filetransfer._tcp.local.",
                addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
                port=port,
                properties={},
            )
            self.zeroconf.register_service(info)
            print(f"Registered service: {name} on port {port}")
        except Exception as e:
            print(f"Failed to register service: {e}")

    def discover_peers(self):
        """Start the service browser to discover peers."""
        class MyListener:
            def __init__(self, peers):
                self.peers = peers

            def add_service(self, zeroconf, type, name):
                """Handle discovery of a new peer."""
                info = zeroconf.get_service_info(type, name)
                if info and info.addresses:
                    peer_address = socket.inet_ntoa(info.addresses[0])
                    self.peers[name] = {
                        "address": peer_address,
                        "port": info.port,
                    }
                    print(f"Discovered peer: {name} at {peer_address}:{info.port}")

            def remove_service(self, zeroconf, type, name):
                """Handle removal of a peer."""
                if name in self.peers:
                    del self.peers[name]
                    print(f"Peer {name} has been removed.")

            def update_service(self, zeroconf, type, name):
                """Handle service updates (optional)."""
                pass

        if self.running:
            print("Peer discovery is already running.")
            return

        # Create the listener and browser
        listener = MyListener(self.peers)
        self.browser = ServiceBrowser(self.zeroconf, "_filetransfer._tcp.local.", listener)
        self.running = True

        # Start discovery in a separate thread
        def run_browser():
            try:
                while self.running:
                    time.sleep(1)  # Avoid busy-waiting, let the browser handle events
            except Exception as e:
                print(f"Discovery thread error: {e}")
            finally:
                print("Peer discovery stopped.")

        discovery_thread = threading.Thread(target=run_browser, daemon=True)
        discovery_thread.start()

    def get_peers(self):
        """Return the current list of discovered peers."""
        return self.peers

    def stop_discovery(self):
        """Stop the peer discovery process."""
        self.running = False
        self.zeroconf.close()
        print("Zeroconf closed and discovery stopped.")

    def close(self):
        """Safely close the Zeroconf instance."""
        self.stop_discovery()


# Example usage
if __name__ == "__main__":
    discovery = PeerDiscovery()

    # Register this device's service
    discovery.register_service("MyDevice", 5000)

    # Start discovering peers
    discovery.discover_peers()

    # Keep the main thread alive to simulate a running program
    try:
        while True:
            time.sleep(5)
            print("Current peers:", discovery.get_peers())
    except KeyboardInterrupt:
        discovery.close()