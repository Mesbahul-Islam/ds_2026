# Simple configuration for peer discovery

# All nodes listen on this ZeroMQ port
NODE_PORT = 5555

# UDP discovery settings (same subnet)
DISCOVERY_PORT = 50000
DISCOVERY_BROADCAST = "255.255.255.255"
DISCOVERY_INTERVAL = 2  # seconds between broadcast pings

# Status update interval (seconds)
STATUS_INTERVAL = 2
