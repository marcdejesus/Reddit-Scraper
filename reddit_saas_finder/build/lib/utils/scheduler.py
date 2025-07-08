
import schedule
import time
import os
import signal
import sys
from datetime import datetime
from rich.console import Console

console = Console()
PID_DIR = "reddit_saas_finder/run"
PID_FILE = os.path.join(PID_DIR, "scheduler.pid")
STATUS_FILE = os.path.join(PID_DIR, "scheduler_status.log")

class TaskScheduler:
    """
    Manages the background scheduling of data scraping and processing tasks.

    This class handles starting, stopping, and checking the status of a recurring
    background job that runs the main data pipeline.
    """
    def __init__(self):
        """Initializes the TaskScheduler, ensuring the run directory exists."""
        os.makedirs(PID_DIR, exist_ok=True)

    def run_scraping_and_processing(self):
        """
        The core task executed by the scheduler.

        This function runs the data pipeline, which includes scraping new data
        and processing it to find pain points. It also logs the status of each
        run to a status file.
        """
        from utils.performance import PerformanceOptimizer
        
        console.log("Scheduler: Running scraping and processing task...")
        try:
            # Using batch_process_pain_points as it combines scraping and processing
            optimizer = PerformanceOptimizer()
            optimizer.batch_process_pain_points(batch_size=200) # Using a default batch size
            with open(STATUS_FILE, "w") as f:
                f.write(f"Last run: {datetime.now().isoformat()}\nStatus: Success")
            console.log("Scheduler: Task finished successfully.")
        except Exception as e:
            console.log(f"Scheduler: Task failed with error: {e}")
            with open(STATUS_FILE, "w") as f:
                f.write(f"Last run: {datetime.now().isoformat()}\nStatus: Failed\nError: {e}")


    def start(self, interval_hours: int):
        """
        Starts the scheduler as a long-running foreground process.

        This method is intended to be run as a background task by the user (e.g.,
        using `&` in the shell). It registers the main task to run at the
        specified interval.

        Args:
            interval_hours (int): The interval in hours at which to run the task.
        """
        if os.path.exists(PID_FILE):
            console.print("[yellow]Scheduler is already running.[/yellow]")
            return

        # Simple daemonization using os.fork is platform specific.
        # This implementation will run in the foreground but is easily backgrounded by the user (e.g. `... &`)
        # A PID file is used to manage state for stop/status commands.
        
        pid = os.getpid()
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        
        console.print(f"[green]Starting scheduler with PID {pid}...[/green]")
        console.print(f"Scheduling job every {interval_hours} hours.")
        
        schedule.every(interval_hours).hours.do(self.run_scraping_and_processing)

        try:
            while True:
                schedule.run_pending()
                time.sleep(60) # Check every minute
        except KeyboardInterrupt:
            console.print("\n[yellow]Scheduler stopped by user.[/yellow]")
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops a running scheduler process by reading its PID and sending a signal.
        """
        if not os.path.exists(PID_FILE):
            console.print("[yellow]Scheduler is not running.[/yellow]")
            return

        with open(PID_FILE, 'r') as f:
            pid = int(f.read())

        try:
            os.kill(pid, signal.SIGTERM)
            console.print(f"[green]Sent stop signal to scheduler with PID {pid}.[/green]")
        except ProcessLookupError:
            console.print(f"[yellow]Scheduler process with PID {pid} not found. It might have already stopped.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error stopping scheduler: {e}[/red]")
        finally:
            os.remove(PID_FILE)
            if os.path.exists(STATUS_FILE):
                 os.remove(STATUS_FILE)


    def get_status(self):
        """
        Checks if the scheduler is running and displays its status.

        It checks for the existence of the PID file and whether the process
        is active. It also displays the content of the last run's status file.
        """
        if not os.path.exists(PID_FILE):
            console.print("[bold red]Scheduler is not running.[/bold red]")
            return

        with open(PID_FILE, 'r') as f:
            pid = int(f.read())

        try:
            os.kill(pid, 0) # Check if process exists
        except OSError:
            console.print("[yellow]Scheduler PID file found, but process is not running. Cleaning up...[/yellow]")
            os.remove(PID_FILE)
            console.print("[bold red]Scheduler is not running.[/bold red]")
        else:
            console.print(f"[bold green]Scheduler is running with PID {pid}.[/bold green]")
            if schedule.jobs:
                console.print(f"Next run: {schedule.next_run}")
            else:
                 console.print("No jobs scheduled.") # This part of status is tricky as it's in a different process.
            
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    console.print("\n--- Last Run Status ---")
                    console.print(f.read()) 