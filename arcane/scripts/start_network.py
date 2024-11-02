
import asyncio
import logging
from arcane.network.network_manager import NetworkManager

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    host = "0.0.0.0"  # Listen on all interfaces
    port = 12345
    token = "secret-token"  # Example token for authentication

    network_manager = NetworkManager(host, port, token)
    await network_manager.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped manually.")
