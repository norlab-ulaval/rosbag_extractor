"""Utility functions used across multiple rosbag extraction modules."""

import math
from collections import deque
import numpy as np
from scipy.spatial.transform import Rotation


class TFBuffer:
    """Transform buffer for TF tree management without ROS2 dependencies."""
    
    def __init__(self):
        self.transforms = {}  # {(parent, child): 4x4 matrix}
        self._path_cache = {}  # {(source, target): path}
        self._known_edges = set()
        
    def set_transform(self, parent_frame, child_frame, translation, rotation):
        """Add or update a transform."""
        # Convert to 4x4 matrix
        T = np.eye(4)
        T[:3, :3] = Rotation.from_quat(rotation).as_matrix()
        T[:3, 3] = translation
        self.transforms[(parent_frame, child_frame)] = T
        if (parent_frame, child_frame) not in self._known_edges:
            self._known_edges.add((parent_frame, child_frame))
            self._path_cache.clear()
        
    def lookup_transform(self, target_frame, source_frame):
        """Look up transform from source_frame to target_frame."""
        if target_frame == source_frame:
            return np.array([0., 0., 0.]), np.array([0., 0., 0., 1.])
        
        cache_key = (source_frame, target_frame)
        if cache_key not in self._path_cache:
            self._path_cache[cache_key] = self._find_path(target_frame, source_frame)
            
        if self._path_cache[cache_key] is None:
            raise Exception(f"Cannot find transform from {source_frame} to {target_frame}")
            
        return self._compose_path(self._path_cache[cache_key])
        
    def _find_path(self, target_frame, source_frame):
        """BFS to find path from source to target frame."""
        queue = deque([(source_frame, [])])
        visited = {source_frame}
        
        while queue:
            current, path = queue.popleft()
            if current == target_frame:
                return path
                
            for parent, child in self.transforms:
                if parent == current and child not in visited:
                    visited.add(child)
                    queue.append((child, path + [(parent, child, False)]))
                elif child == current and parent not in visited:
                    visited.add(parent)
                    queue.append((parent, path + [(parent, child, True)]))
        return None
        
    def _compose_path(self, path):
        """Compose transforms along a path."""
        result = np.eye(4)
        
        for parent, child, inverse in path:
            T = self.transforms.get((parent, child))
            if T is None:
                raise Exception(f"Transform {parent}->{child} not available")
            
            result = result @ (np.linalg.inv(T) if inverse else T)
        
        # Extract translation and rotation
        trans = result[:3, 3]
        rot = Rotation.from_matrix(result[:3, :3]).as_quat()
        return trans, rot


def euler_from_quaternion(x, y, z, w):
    """
    Convert quaternion to Euler angles (roll, pitch, yaw).
    
    Args:
        x, y, z, w: Quaternion components
        
    Returns:
        tuple: (roll, pitch, yaw) in radians
    """
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw
