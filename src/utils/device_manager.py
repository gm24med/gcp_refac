"""
Device management for GPU/CPU handling
"""

import torch
import logging
from typing import Dict, Any
from .exceptions import DeviceError


class DeviceManager:
    """Manages device selection and configuration - max 50 lines"""
    
    def __init__(self):
        """Initialize device manager"""
        self.logger = logging.getLogger(__name__)
        self.device_info = self._detect_devices()
    
    def _detect_devices(self) -> Dict[str, Any]:
        """Detect available devices"""
        info = {
            'cuda_available': torch.cuda.is_available(),
            'device_count': 0,
            'devices': []
        }
        
        if info['cuda_available']:
            info['device_count'] = torch.cuda.device_count()
            info['devices'] = [
                {
                    'id': i,
                    'name': torch.cuda.get_device_name(i),
                    'memory': torch.cuda.get_device_properties(i).total_memory / 1e9
                }
                for i in range(info['device_count'])
            ]
        
        return info
    
    def get_best_device(self) -> str:
        """Get the best available device"""
        if self.device_info['cuda_available']:
            # Select GPU with most memory
            best_gpu = max(self.device_info['devices'], key=lambda x: x['memory'])
            device = f"cuda:{best_gpu['id']}"
            self.logger.info(f"Selected device: {device} ({best_gpu['name']})")
            return device
        else:
            self.logger.info("CUDA not available, using CPU")
            return "cpu"
    
    def get_torch_dtype(self, device: str) -> torch.dtype:
        """Get appropriate torch dtype for device"""
        return torch.float16 if device.startswith('cuda') else torch.float32
    
    def validate_device(self, device: str) -> bool:
        """Validate if device is available"""
        if device == "cpu":
            return True
        elif device.startswith("cuda:"):
            gpu_id = int(device.split(":")[1])
            return gpu_id < self.device_info['device_count']
        else:
            raise DeviceError(f"Invalid device format: {device}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return self.device_info.copy() 