"""Utility functions used across multiple rosbag extraction modules."""

from collections import deque
import numpy as np
from scipy.spatial.transform import Rotation


class Colors:
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def extract_timestamp(msg):
    if hasattr(msg, 'header'):
        return int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec)
    return None


def extract_point(point_msg, prefix=""):
    return {
        f"{prefix}x": point_msg.x,
        f"{prefix}y": point_msg.y,
        f"{prefix}z": point_msg.z
    }


def extract_vector3(vec_msg, prefix=""):
    return {
        f"{prefix}x": vec_msg.x,
        f"{prefix}y": vec_msg.y,
        f"{prefix}z": vec_msg.z
    }


def extract_orientation(quat_msg, euler=False, prefix=""):
    if euler:
        quat = [quat_msg.x, quat_msg.y, quat_msg.z, quat_msg.w]
        roll, pitch, yaw = Rotation.from_quat(quat).as_euler("xyz", degrees=False)
        return {
            f"{prefix}roll": roll,
            f"{prefix}pitch": pitch,
            f"{prefix}yaw": yaw
        }
    else:
        return {
            f"{prefix}qx": quat_msg.x,
            f"{prefix}qy": quat_msg.y,
            f"{prefix}qz": quat_msg.z,
            f"{prefix}qw": quat_msg.w
        }


def extract_pose(pose_msg, euler=False, prefix=""):
    result = {}
    result.update(extract_point(pose_msg.position, prefix=prefix))
    result.update(extract_orientation(pose_msg.orientation, euler=euler, prefix=prefix))
    return result


def extract_twist(twist_msg, prefix="vel_"):
    result = {}
    result.update({
        f"{prefix}x": twist_msg.linear.x,
        f"{prefix}y": twist_msg.linear.y,
        f"{prefix}z": twist_msg.linear.z,
    })
    result.update({
        f"{prefix}roll": twist_msg.angular.x,
        f"{prefix}pitch": twist_msg.angular.y,
        f"{prefix}yaw": twist_msg.angular.z,
    })
    return result


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
            raise ValueError(f"Cannot find transform from {source_frame} to {target_frame}")
            
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
                raise KeyError(f"Transform {parent}->{child} not available")
            
            result = result @ (np.linalg.inv(T) if inverse else T)
        
        # Extract translation and rotation
        trans = result[:3, 3]
        rot = Rotation.from_matrix(result[:3, :3]).as_quat()
        return trans, rot
