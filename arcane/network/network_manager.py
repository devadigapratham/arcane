import asyncio
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class NetworkManager:
    """
    Handles network communication between nodes for distributed training.
    """
    def __init__(self, host: str, port: int, token: str):
        self.host = host
        self.port = port
        self.token = token
        self.connections: Dict[str, Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}

    async def start_server(self):
        """
        Start the server to listen for incoming connections.
        """
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f"Server started on {addr}")

        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle an incoming connection from a node.
        """
        try:
            # Authenticate the connection
            peername = writer.get_extra_info('peername')
            logger.info(f"Connection established with {peername}")

            received_token = await reader.read(100)
            if received_token.decode() != self.token:
                logger.warning(f"Authentication failed for {peername}")
                writer.close()
                await writer.wait_closed()
                return

            # Add to active connections
            self.connections[str(peername)] = (reader, writer)
            logger.info(f"Authenticated connection from {peername}")

            # Start listening for incoming data
            await self.listen_to_node(reader, writer)

        except asyncio.CancelledError:
            logger.info("Connection handling task cancelled.")
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Connection closed with {peername}")

    async def listen_to_node(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Listen for messages from a connected node.
        """
        while True:
            try:
                data = await reader.read(100)
                if not data:
                    break
                logger.info(f"Received data from node: {data.decode()}")
            except asyncio.IncompleteReadError:
                logger.warning("Connection lost while reading data.")
                break
            except Exception as e:
                logger.error(f"Error reading data: {e}")
                break

    async def send_message(self, node: str, message: str):
        """
        Send a message to a specific node.
        """
        if node in self.connections:
            reader, writer = self.connections[node]
            writer.write(message.encode())
            await writer.drain()
            logger.info(f"Sent message to {node}: {message}")
        else:
            logger.warning(f"Node not found: {node}")


