import os
import sys
import json
from PySide6.QtCore import QUrl, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QIcon

from src.controllers.resource import Resources  
from src.controllers.tasks import ProcessInfo


class ProcessThread(QThread):
    update_process_signal = Signal(list)

    def __init__(self, process_info):
        super().__init__()
        self.process_info = process_info

    def run(self):
        while True:
            self.process_info.fetch_process_info()
            self.update_process_signal.emit(self.process_info.processes)
            self.msleep(1000)


class ResourceThread(QThread):
    update_cpu_signal = Signal(float)
    update_memory_signal = Signal(object)

    def __init__(self, resources):
        super().__init__()
        self.resources = resources

    def run(self):
        while True:
            cpu_usage = self.resources.get_cpu_usage()
            self.update_cpu_signal.emit(cpu_usage)

            total_memory, used_memory, free_memory, memory_percent = self.resources.get_memory_usage()
            memory_data = {
                "totalMemory": total_memory,
                "usedMemory": used_memory,
                "freeMemory": free_memory,
                "memoryPercent": memory_percent
            }
            self.update_memory_signal.emit(memory_data)
            self.msleep(1000)


class CreateWindow:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.window = QMainWindow()
        self.window.setWindowTitle("Задачный диспетчер")
        self.window.setGeometry(100, 100, 1000, 600)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.window.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        self.central_widget.setLayout(self.layout)
        self.window.setCentralWidget(self.central_widget)

        self.channel = QWebChannel()
        self.resources = Resources()
        self.channel.registerObject("resources", self.resources)

        self.process_info = ProcessInfo()
        self.channel.registerObject("process_info", self.process_info)

        self.web_view.page().setWebChannel(self.channel)
        self.load_html()

        self.resource_thread = ResourceThread(self.resources)
        self.resource_thread.update_cpu_signal.connect(self.update_cpu)
        self.resource_thread.update_memory_signal.connect(self.update_memory)
        self.resource_thread.start()

        self.process_thread = ProcessThread(self.process_info)
        self.process_thread.update_process_signal.connect(self.update_processes)
        self.process_thread.start()

    def load_html(self):
        html_file = os.path.join(os.path.dirname(__file__), "templates", "taskmenager.html")
        html_file = os.path.normpath(html_file)

        if os.path.exists(html_file):
            self.web_view.setUrl(QUrl.fromLocalFile(html_file))
        else:
            print(f"HTML-файл не найден: {html_file}")

    def update_cpu(self, cpu_usage):
        self.web_view.page().runJavaScript(f"updateCPUUsage({cpu_usage});")

    def update_memory(self, memory_data):
        self.web_view.page().runJavaScript(f"updateMemoryUsage({json.dumps(memory_data)});")

    def update_processes(self, processes):
        self.web_view.page().runJavaScript(f"updateProcessInfo({json.dumps(processes)});")

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


