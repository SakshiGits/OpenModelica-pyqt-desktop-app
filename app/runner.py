import subprocess
import os
from PyQt6.QtCore import QThread, pyqtSignal


class SimulationRunner(QThread):
    """
    Runs the OpenModelica executable in a separate thread
    so the GUI does not freeze.
    """

    # Signals to communicate with UI
    finished = pyqtSignal(int)          # Exit code
    output_received = pyqtSignal(str)   # Output logs
    error_occurred = pyqtSignal(str)    # Errors

    def __init__(self, executable_path: str, start_time: int, stop_time: int):
        super().__init__()
        self.executable_path = executable_path
        self.start_time = start_time
        self.stop_time = stop_time

    def run(self):
        """Executes the simulation."""

        # Build command
        args = [
            self.executable_path,
            "-startTime", str(self.start_time),
            "-stopTime", str(self.stop_time),
            "-stepSize", "0.01"
        ]

        # Get working directory (important for DLLs)
        working_dir = os.path.dirname(self.executable_path) or "."

        # Show command in UI
        self.output_received.emit(f"Command: {' '.join(args)}")
        self.output_received.emit(f"Working Directory: {working_dir}\n")

        try:
            # 🔥 Ensure local DLLs are used (portable solution)
            env = os.environ.copy()
            env["PATH"] = working_dir + ";" + env["PATH"]

            # Start process
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=working_dir,
                env=env
            )

            # Read output in real-time
            for line in process.stdout:
                if line:
                    self.output_received.emit(line.strip())

            # Wait for process to finish
            process.wait()

            # Send exit code to UI
            return_code = process.returncode
            self.finished.emit(return_code if return_code is not None else -1)

        except FileNotFoundError:
            self.error_occurred.emit("Error: Executable not found.")
            self.finished.emit(-1)

        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")
            self.finished.emit(-1)
