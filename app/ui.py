import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QSpinBox,
                             QTextEdit, QMessageBox, QFileDialog, QGroupBox,
                             QFormLayout)
from PyQt6.QtGui import QFont

# Import the runner logic
from app.runner import SimulationRunner


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.runner = None
        self.init_ui()

    def init_ui(self):
        """Initialize the User Interface."""
        self.setWindowTitle("OpenModelica Controller")
        self.resize(600, 500)

        # Central Widget & Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Configuration Section ---
        config_group = QGroupBox("Simulation Parameters")
        form_layout = QFormLayout()

        # 1. Executable Path
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select TwoConnectedTanks.exe...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_executable)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        form_layout.addRow("Executable Path:", path_layout)

        # 2. Start Time
        self.start_time_input = QSpinBox()
        self.start_time_input.setRange(0, 3)
        self.start_time_input.setValue(0)
        form_layout.addRow("Start Time (0-3):", self.start_time_input)

        # 3. Stop Time
        self.stop_time_input = QSpinBox()
        self.stop_time_input.setRange(1, 4)
        self.stop_time_input.setValue(4)
        form_layout.addRow("Stop Time (1-4):", self.stop_time_input)

        config_group.setLayout(form_layout)
        main_layout.addWidget(config_group)

        # --- Run Button ---
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.run_btn.setStyleSheet(
            "background-color: #2E86C1; color: white; padding: 10px; border-radius: 5px;")
        self.run_btn.clicked.connect(self.run_simulation)
        main_layout.addWidget(self.run_btn)

        # --- Output Log ---
        log_group = QGroupBox("Simulation Log")
        log_layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 9))
        self.log_output.setStyleSheet(
            "background-color: #F4F6F7; color: #333;")

        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

    def browse_executable(self):
        """Open file dialog to select .exe file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Executable",
            "",
            "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.path_input.setText(file_path)

    def validate_inputs(self) -> bool:
        """Validate user inputs."""
        path = self.path_input.text().strip()
        start = self.start_time_input.value()
        stop = self.stop_time_input.value()

        if not os.path.isfile(path):
            QMessageBox.warning(self, "Input Error",
                                "Please select a valid executable file.")
            return False

        if not (0 <= start < stop < 5):
            QMessageBox.critical(
                self,
                "Constraint Error",
                f"Invalid times: {start} to {stop}\nCondition: 0 <= start < stop < 5"
            )
            return False

        return True

    def run_simulation(self):
        """Run simulation when button is clicked."""
        if not self.validate_inputs():
            return

        # UI updates
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running...")
        self.log_output.clear()

        exe_path = self.path_input.text()
        start = self.start_time_input.value()
        stop = self.stop_time_input.value()

        # Start worker thread
        self.runner = SimulationRunner(exe_path, start, stop)
        self.runner.output_received.connect(self.log_output.append)
        self.runner.error_occurred.connect(self.log_output.append)
        self.runner.finished.connect(self.simulation_finished)
        self.runner.start()

    def simulation_finished(self, exit_code):
        """Handle simulation completion."""
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run Simulation")

        if exit_code == 0:
            self.log_output.append(
                "\n[SUCCESS] Simulation completed successfully.")
        else:
            self.log_output.append(
                f"\n[FAILED] Simulation exited with code {exit_code}.")
