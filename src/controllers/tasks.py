from PySide6.QtCore import QObject, Slot
import psutil
import json


class ProcessInfo(QObject):
    def __init__(self):
        super().__init__()
        self.processes = []

    def fetch_process_info(self):
        self.processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                process_info = {
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent']
                }
                self.processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    @Slot(int, result=bool)
    def kill_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Ошибка завершения процесса с PID {pid}: {e}")
            return False

    @Slot(result=str)
    def get_processes(self):
        self.fetch_process_info()
        return json.dumps(self.processes)
