import asyncio
import logging
from arcane.monitoring.resource_monitor import ResourceMonitor

logger = logging.getLogger(__name__)

class WorkerNode:
    """
    Worker node responsible for receiving and executing training jobs from the master node.
    """
    def __init__(self, master_host: str, master_port: int, token: str):
        self.master_host = master_host
        self.master_port = master_port
        self.token = token
        self.resource_monitor = ResourceMonitor()

    async def connect_to_master(self):
        """
        Connect to the master node and authenticate.
        """
        self.reader, self.writer = await asyncio.open_connection(self.master_host, self.master_port)

        # Send authentication token
        self.writer.write(self.token.encode())
        await self.writer.drain()

        # Verify authentication
        logger.info("Connected to master node")
        await asyncio.gather(self.listen_for_jobs(), self.monitor_resources())

    async def listen_for_jobs(self):
        """
        Listen for incoming training jobs from the master node.
        """
        while True:
            try:
                message = await self.reader.read(100)
                if not message:
                    break

                command, *params = message.decode().split("|")
                if command == "JOB":
                    job_id, job_data = params
                    await self.execute_job(job_id, job_data)
                elif command == "STOP":
                    logger.info("Received stop signal")
                    break
            except asyncio.IncompleteReadError:
                logger.warning("Connection to master lost.")
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                break
    
    async def execute_job(self, job_id: str, job_data: str):
        """
        Execute the assigned training job.
        """
        logger.info(f"Executing job {job_id} with data: {job_data}")

        try:
            self.current_job_id = job_id
            self.stop_requested = False  # Add a flag to track stop requests

            for progress in range(0, 101, 20):
                if self.stop_requested:
                    logger.info(f"Job {job_id} stopped by master")
                    await self.send_progress_update(job_id, -1)  # Mark as stopped
                    return
                await asyncio.sleep(2)  # Simulate time-consuming job
                await self.send_progress_update(job_id, progress)

            await self.send_progress_update(job_id, 100)  # Mark as complete
            logger.info(f"Job {job_id} completed successfully")
        except Exception as e:
            logger.error(f"Error executing job {job_id}: {e}")
            await self.send_progress_update(job_id, -1)  # Mark as failed

    async def handle_incoming_messages(self):
        """
        Listen for incoming messages and handle them appropriately.
        """
        while True:
            try:
                message = await self.reader.read(200)
                if not message:
                    break

                message_type, *data = message.decode().split("|")
                if message_type == "STOP":
                    job_id = data[0]
                    if job_id == self.current_job_id:
                        self.stop_requested = True  # Set the flag to stop the current job
                # Handle other message types...
            except asyncio.IncompleteReadError:
                logger.warning("Connection lost with master node")
                break
            except Exception as e:
                logger.error(f"Error handling incoming message: {e}")

    async def send_progress_update(self, job_id: str, progress: int):
        """
        Send a progress update to the master node.
        """
        status = "running" if 0 <= progress < 100 else ("completed" if progress == 100 else "failed")
        message = f"PROGRESS|{job_id}|{progress}|{status}"
        self.writer.write(message.encode())
        await self.writer.drain()
        logger.info(f"Sent progress update for job {job_id}: {progress}% ({status})")

    async def monitor_resources(self):
        """
        Monitor system resources and send periodic updates to the master node.
        """
        while True:
            resource_usage = self.resource_monitor.get_resource_usage()
            try:
                message = f"RESOURCE|{resource_usage}"
                self.writer.write(message.encode())
                await self.writer.drain()
                logger.info("Sent resource usage update")
            except Exception as e:
                logger.error(f"Failed to send resource usage: {e}")
                break

            await asyncio.sleep(5)  # Adjust the interval as needed

    async def start(self):
        """
        Start the worker node.
        """
        await self.connect_to_master()
