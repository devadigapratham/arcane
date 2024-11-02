import psutil
import logging
from typing import Dict, Any, Optional

try:
    import pynvml
    pynvml.nvmlInit()
except ImportError:
    pynvml = None
    logging.warning("GPU monitoring not available. Install nvidia-ml-py3 for GPU metrics.")

logger = logging.getLogger(__name__)

class ResourceMonitor:
    """
    Monitors system resource usage including CPU, memory, and GPU (if available).
    """
    def __init__(self):
        self.gpu_available = pynvml is not None

    def get_cpu_memory_usage(self) -> Dict[str, Any]:
        """
        Get current CPU and memory usage.
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
        }

    def get_gpu_usage(self) -> Optional[Dict[str, Any]]:
        """
        Get current GPU usage if GPU is available.
        """
        if not self.gpu_available:
            return None

        gpu_info = {}
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpu_info[f"gpu_{i}_util"] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                gpu_info[f"gpu_{i}_mem"] = pynvml.nvmlDeviceGetMemoryInfo(handle).used / 1024**2  # MB
        except Exception as e:
            logger.warning(f"Failed to get GPU usage: {e}")
            return None

        return gpu_info

    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get all resource usage metrics.
        """
        usage = self.get_cpu_memory_usage()
        if self.gpu_available:
            gpu_usage = self.get_gpu_usage()
            if gpu_usage:
                usage.update(gpu_usage)
        return usage
