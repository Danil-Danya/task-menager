import sys
import PySide6
from PySide6.QtWidgets import QApplication
from client.window import CreateWindow  # Убедитесь, что путь правильный

if __name__ == "__main__":
    window = CreateWindow()
    window.run()
