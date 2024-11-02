import asyncio
import logging
from arcane.training.master_node import MasterNode

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    master_host = "0.0.0.0"
    master_port = 12345
    token = "secret-token"

    master_node = MasterNode(master_host, master_port, token)
    await master_node.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Master node stopped manually.")
