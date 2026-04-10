import sys
from PyQt6.QtWidgets import QApplication
from app.ui import MainWindow


def main():
    """
    Main entry point for the OpenModelica GUI Application.
    """
    app = QApplication(sys.argv)

    # Optional: Set a clean Fusion style for all platforms
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
