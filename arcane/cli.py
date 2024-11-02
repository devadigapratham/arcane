import typer
import asyncio

app = typer.Typer()

BANNER = r"""
                                               
_____ _______   ____ _____    ____   ____      
\__  \\_  __ \_/ ___\\__  \  /    \_/ __ \     
 / __ \|  | \/\  \___ / __ \|   |  \  ___/     
(____  /__|    \___  >____  /___|  /\___  > /\ 
     \/            \/     \/     \/     \/  \/ 
"""

@app.callback(invoke_without_command=True)
def show_banner(ctx: typer.Context):
    """
    Display banner art if no command is provided.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(BANNER)
        typer.echo("Welcome to Arcane CLI - Distributed Training Tool")

@app.command()
def start_master(host: str = "localhost", port: int = 8888, token: str = "my_secure_token", config: str = typer.Option(None, help="The path to the master configuration file")):
    """
    Start the master node.
    """
    # Importing here to avoid unnecessary import if noit running this command
    if config:
        typer.echo(f"Loading configuration from {config}")

    from arcane.training.master_node import MasterNode
    master = MasterNode(host, port, token)
    asyncio.run(master.start())


@app.command()
def start_worker(
    master_host: str = typer.Option("localhost", help="The host of the master node"),
    master_port: int = typer.Option(8888, help="The port of the master node"),
    token: str = typer.Option("my_secure_token", help="The token for authentication"),
    config: str = typer.Option(None, help="The path to the worker configuration file")
):
    """
    Start a worker node and connect to the master.
    """
    if config:
        typer.echo(f"Loading configuration from {config}")

    from arcane.training.worker_node import WorkerNode
    worker = WorkerNode(master_host, master_port, token)
    asyncio.run(worker.start())


class Orchestrator:
    def get_active_jobs(self):
        # Placeholder implementation
        return [{"id": "job1", "status": "running"}, {"id": "job2", "status": "completed"}]

    def get_connected_nodes(self):
        # Placeholder implementation
        return [{"id": "node1", "status": "active"}, {"id": "node2", "status": "inactive"}]

@app.command()
def status():
    """Display the current status of all jobs and worker nodes."""
    try:
        # Example status retrieval logic
        orchestrator = Orchestrator()
        jobs = orchestrator.get_active_jobs()
        nodes = orchestrator.get_connected_nodes()

        if not jobs and not nodes:
            typer.echo("No active jobs or connected nodes.")
        else:
            typer.echo(f"Active Jobs: {len(jobs)}")
            for job in jobs:
                typer.echo(f"Job ID: {job['id']}, Status: {job['status']}")

            typer.echo(f"Connected Worker Nodes: {len(nodes)}")
            for node in nodes:
                typer.echo(f"Node ID: {node['id']}, Status: {node['status']}")

    except Exception as e:
        typer.echo(f"Error retrieving status: {e}")

@app.command()
def stop(job_id: str, host: str = "localhost", port: int = 8888, token: str = "my_secure_token"):
    """
    Stop a specific job by job ID.
    """
    from arcane.training.master_node import MasterNode
    master = MasterNode(host, port, token)
    master.stop_job(job_id)

if __name__ == "__main__":
    app()
