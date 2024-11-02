import asyncio
import logging
from arcane.network.network_manager import NetworkManager

logger = logging.getLogger(__name__)

class MasterNode:
    """
    Master node responsible for orchestrating distributed training across multiple workers.
    """
    def __init__(self, host: str, port: int, token: str):
        self.network_manager = NetworkManager(host, port, token)
        self.job_counter = 0
        self.jobs = []
        self.host = host 
        self.job_status = {}

    async def start(self):
        """
        Start the master node server.
        """
        await self.network_manager.start_server()

    async def distribute_job(self, job_data: str):
        """
        Distribute a training job to all connected workers.
        """
        for node in self.network_manager.connections:
            try:
                await self.network_manager.send_message(node, f"JOB|{self.job_counter}|{job_data}")
                logger.info(f"Assigned job {self.job_counter} to worker {node}")
            except Exception as e:
                logger.error(f"Failed to assign job {self.job_counter} to {node}: {e}")
        
        self.job_counter += 1

    async def stop_all_jobs(self):
        """
        Send a stop signal to all connected workers.
        """
        for node in self.network_manager.connections:
            try:
                await self.network_manager.send_message(node, "STOP")
                logger.info(f"Sent stop signal to worker {node}")
            except Exception as e:
                logger.error(f"Failed to send stop signal to {node}: {e}")

    async def monitor_progress(self):
        """
        Monitor the progress of all active jobs and resource usage.
        """
        while True:
            for node in self.network_manager.connections:
                reader, _ = self.network_manager.connections[node]
                try:
                    update = await reader.read(200)
                    message_type, *data = update.decode().split("|")

                    if message_type == "PROGRESS":
                        job_id, progress, status = data
                        self.job_status[job_id] = {"node": node, "progress": progress, "status": status}
                        logger.info(f"Job {job_id} on {node}: {progress}% ({status})")

                    elif message_type == "RESOURCE":
                        resource_usage = eval(data[0])  # Convert the string back to a dictionary
                        logger.info(f"Resource usage from {node}: {resource_usage}")
                except asyncio.IncompleteReadError:
                    logger.warning(f"Lost connection to {node}")
                except Exception as e:
                    logger.error(f"Error receiving update from {node}: {e}")
            await asyncio.sleep(2)  # Adjust the interval as needed

    def display_job_status(self):
        """
        Display the current status of all jobs.
        """
        for job_id, status_info in self.job_status.items():
            node = status_info["node"]
            progress = status_info["progress"]
            status = status_info["status"]
            print(f"Job {job_id}: {progress}% ({status}) on Node {node}")

    async def send_stop_signal(self, job_id: str):
        """
        Send a stop signal to all worker nodes for a specific job.
        """
        stop_message = f"STOP|{job_id}"
        for node, (reader, writer) in self.network_manager.connections.items():
            try:
                writer.write(stop_message.encode())
                await writer.drain()
                logger.info(f"Sent stop signal for job {job_id} to node {node}")
            except Exception as e:
                logger.error(f"Error sending stop signal to node {node}: {e}")

    def stop_job(self, job_id: str):
        """
        Stop a specific job by sending stop signals to all worker nodes.
        """
        job = self.find_job_by_id(job_id)
        if job:
            # Update the job status to 'stopped'
            job['status'] = 'stopped'
            # Save the updated job status to the storage
            self.update_job_status(job)
        else:
            print(f"Job with ID {job_id} not found.")

    def find_job_by_id(self, job_id):
        """
        Find a job by its ID.
        """
        for job in self.jobs:
            if job['id'] == job_id:
                return job
        return None
