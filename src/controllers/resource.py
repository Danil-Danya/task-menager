import psutil
import pynvml
from PySide6.QtCore import QObject, Slot

class Resources(QObject):
    def __init__(self):
        super().__init__()
        pynvml.nvmlInit()

    @Slot()
    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    @Slot()
    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024 ** 3)
        used_memory = memory.used / (1024 ** 3)
        free_memory = memory.available / (1024 ** 3)
        memory_percent = memory.percent
        return total_memory, used_memory, free_memory, memory_percent

    @Slot()
    def get_gpu_usage(self):
        device_count = pynvml.nvmlDeviceGetCount()
        gpu_info = []

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            gpu_info.append({
                "name": pynvml.nvmlDeviceGetName(handle),
                "gpu_util": utilization.gpu,
                "temperature": temperature
            })

        return gpu_info

    @Slot()
    def get_disk_info(self):
        disks = psutil.disk_partitions()
        disk_count = len(disks)
        
        total_disk_usage = 0  
        total_disk_size = 0  
        total_disk_used = 0  

        for disk in disks:
            disk_usage = psutil.disk_usage(disk.mountpoint)  
            total_disk_usage += disk_usage.percent
            total_disk_size += disk_usage.total
            total_disk_used += disk_usage.used
        
        average_disk_usage = total_disk_usage / disk_count if disk_count else 0

        return disk_count, average_disk_usage, total_disk_size / (1024 ** 3), total_disk_used / (1024 ** 3)

    @Slot()
    def get_memory_info(self):
        memory = psutil.virtual_memory()

        total_memory = memory.total / (1024 ** 3)
        used_memory = memory.used / (1024 ** 3)
        memory_percent = memory.percent

        return total_memory, used_memory, memory_percent

    @Slot()
    def get_network_usage(self):
        network_io = psutil.net_io_counters()
        upload_speed = (network_io.bytes_sent * 8) / (1024 ** 2) 
        download_speed = (network_io.bytes_recv * 8) / (1024 ** 2)  

        return {
            "upload_mbps": upload_speed,
            "download_mbps": download_speed
        }

    def __del__(self):
        pynvml.nvmlShutdown()


