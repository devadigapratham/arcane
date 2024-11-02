import asyncio
import logging
from arcane.training.worker_node import WorkerNode

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    master_host = "127.0.0.1"  # IP address of the master node
    master_port = 12345
    token = "secret-token"

    worker_node = WorkerNode(master_host, master_port, token)
    await worker_node.connect_to_master()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker node stopped manually.")
