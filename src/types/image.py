import cv2
import numpy as np
import pypylon.pylon as pylon
from dataclasses import dataclass
from glymur import Jp2k
from tqdm import tqdm

from src.base_extractor import FolderExtractor
from src.utils import extract_timestamp

@dataclass
class CameraCalibration:
    K: np.ndarray
    D: np.ndarray
    P: np.ndarray
    R: np.ndarray
    dist: str
    width: int
    height: int

ENCODINGS = {
    "rgb8": (np.uint8, 3),
    "rgba8": (np.uint8, 4),
    "rgb16": (np.uint16, 3),
    "rgba16": (np.uint16, 4),
    "bgr8": (np.uint8, 3),
    "bgra8": (np.uint8, 4),
    "bgr16": (np.uint16, 3),
    "bgra16": (np.uint16, 4),
    "mono8": (np.uint8, 1),
    "mono16": (np.uint16, 1),
    "8UC1": (np.uint8, 1),
    "8UC2": (np.uint8, 2),
    "8UC3": (np.uint8, 3),
    "8UC4": (np.uint8, 4),
    "8SC1": (np.int8, 1),
    "8SC2": (np.int8, 2),
    "8SC3": (np.int8, 3),
    "8SC4": (np.int8, 4),
    "16UC1": (np.uint16, 1),
    "16UC2": (np.uint16, 2),
    "16UC3": (np.uint16, 3),
    "16UC4": (np.uint16, 4),
    "16SC1": (np.int16, 1),
    "16SC2": (np.int16, 2),
    "16SC3": (np.int16, 3),
    "16SC4": (np.int16, 4),
    "32SC1": (np.int32, 1),
    "32SC2": (np.int32, 2),
    "32SC3": (np.int32, 3),
    "32SC4": (np.int32, 4),
    "32FC1": (np.float32, 1),
    "32FC2": (np.float32, 2),
    "32FC3": (np.float32, 3),
    "32FC4": (np.float32, 4),
    "64FC1": (np.float64, 1),
    "64FC2": (np.float64, 2),
    "64FC3": (np.float64, 3),
    "64FC4": (np.float64, 4),
    "bayer_rggb8": (np.uint8, 1),
    "bayer_bggr8": (np.uint8, 1),
    "bayer_gbrg8": (np.uint8, 1),
    "bayer_grbg8": (np.uint8, 1),
    "bayer_rggb16": (np.uint16, 1),
    "bayer_bggr16": (np.uint16, 1),
    "bayer_gbrg16": (np.uint16, 1),
    "bayer_grbg16": (np.uint16, 1),
}

FALLBACK_IMAGE_SIZE = (1200, 1920, 1)


class ImageExtractor(FolderExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "images"
        self.ext = self.args.get("extension", "png")
        self.quality_factor = self.args.get("quality_factor", 1.0)
        self.basler_decompress = self.args.get("basler_decompress", False)
        self.convert_12to8bits = self.args.get("convert_12to8bits", False)
        self.debayer = self.args.get("debayer", False)
        self.rectify = self.args.get("rectify", False)
        self.scale = self.args.get("scale", 1.0)
        self.gray_scale = self.args.get("gray_scale", False)
    
    def _pre_extract(self, reader):
        self.calib = self._get_camera_info(reader)
        self._save_camera_calibration(self.calib)
    
    def _post_extract(self, reader):
        if self.args.get("brackets"):
            self._sort_bracket_images(reader)
    
    def _process_message(self, msg, ros_time, msgtype):
        timestamp = extract_timestamp(msg)
        np_image = self._decompress_image(msg) if self.basler_decompress else self._image_to_numpy(msg)
        encoding = getattr(msg, 'encoding', None)
        np_image = self._apply_transformations(np_image, encoding)
        self._save_image(np_image, timestamp)
        return True
    
    def _apply_transformations(self, image, encoding):
        if self.convert_12to8bits and image.dtype == np.uint16:
            image = (image / 16).astype(np.uint8)
        if self.debayer and encoding and "bayer" in encoding:
            image = cv2.cvtColor(image, cv2.COLOR_BayerRG2RGB)
        if self.rectify:
            if self.calib.dist in ["equidistant", "fisheye"]:
                image = cv2.fisheye.undistortImage(image, self.calib.K, self.calib.D, Knew=self.calib.K)
            else:
                image = cv2.undistort(image, self.calib.K, self.calib.D)
        if self.scale != 1.0:
            image = cv2.resize(image, (0, 0), fx=self.scale, fy=self.scale)
        if self.gray_scale and len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _save_image(self, image, timestamp):
        output_file = self.save_folder / f"{int(timestamp):d}.{self.ext}"
        if self.quality_factor < 1.0 and self.ext.lower() == "jpg":
            Jp2k(str(output_file), data=image, cratios=[self.quality_factor])
        else:
            cv2.imwrite(str(output_file), image)
    
    def _save_camera_calibration(self, calib):
        if calib is None or calib.K is None:
            return
        
        calibration_file = self.save_folder / "camera_calibration.yaml"
        
        fs = cv2.FileStorage(str(calibration_file), cv2.FILE_STORAGE_WRITE)
        fs.write("image_width", int(calib.width))
        fs.write("image_height", int(calib.height))
        fs.write("camera_matrix", calib.K)
        fs.write("distortion_model", calib.dist)
        fs.write("distortion_coefficients", calib.D)
        fs.write("rectification_matrix", calib.R)
        fs.write("projection_matrix", calib.P)
        fs.release()
        
        print(f"Saved camera calibration to {calibration_file}")
    
    def _get_camera_info(self, reader):
        topic_base = self.topic_name.replace("/compressed", "")
        camera_info_topic = "/".join(topic_base.split("/")[:-1] + ["camera_info"])
        connections = [x for x in reader.connections if x.topic == camera_info_topic]

        if not connections:
            if self.rectify:
                raise ValueError(f"Camera info topic not found for {self.topic_name}")
            return None

        connection, _, rawdata = next(reader.messages(connections=connections))
        camera_info = reader.deserialize(rawdata, connection.msgtype)
        
        K = np.array(camera_info.k if hasattr(camera_info, 'k') else camera_info.K).reshape([3, 3])
        D = np.array(camera_info.d if hasattr(camera_info, 'd') else camera_info.D)
        P = np.array(camera_info.p if hasattr(camera_info, 'p') else camera_info.P).reshape([3, 4])
        R = np.array(camera_info.r if hasattr(camera_info, 'r') else camera_info.R).reshape([3, 3])
        dist = getattr(camera_info, 'distortion_model', 'plumb_bob')
        
        return CameraCalibration(K, D, P, R, dist, camera_info.width, camera_info.height)
    
    def _image_to_numpy(self, msg):
        if hasattr(msg, 'format'):
            np_arr = np.frombuffer(msg.data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)
            if image is None:
                raise ValueError(f"Failed to decode compressed image with format: {msg.format}")
            return image
        
        if msg.encoding not in ENCODINGS:
            raise ValueError(f"Unrecognized encoding: {msg.encoding}")

        dtype_class, channels = ENCODINGS[msg.encoding]
        dtype = np.dtype(dtype_class)
        dtype = dtype.newbyteorder(">" if msg.is_bigendian else "<")
        shape = (msg.height, msg.width, channels)

        data = np.frombuffer(msg.data, dtype=dtype).reshape(shape)
        data.strides = (msg.step, dtype.itemsize * channels, dtype.itemsize)

        if "rgb" in msg.encoding:
            data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        if channels == 1:
            data = data[..., 0]
        return data
    
    def _sort_bracket_images(self, reader):
        topic_base = self.topic_name.replace("/compressed", "")
        metadata_topic = "/".join(topic_base.split("/")[:-1] + ["metadata"])
        brackets = np.array(self.args["brackets"])

        for bracketing_value in brackets:
            (self.save_folder / f"{bracketing_value:.1f}").mkdir(exist_ok=True)

        print(f'Sorting images from folder "{self.save_folder}"')
        connections = [x for x in reader.connections if x.topic == metadata_topic]
        for connection, _, rawdata in tqdm(list(reader.messages(connections=connections))):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = extract_timestamp(msg)
            bracketing_value = brackets[(np.abs(brackets - msg.ExposureTime)).argmin()]
            image_path = self.save_folder / f"{int(timestamp):d}.{self.ext}"
            if image_path.exists():
                image_path.rename(self.save_folder / f"{bracketing_value:.1f}" / image_path.name)

        print(f"Done ! Sorted images to {self.save_folder}")
    
    def _decompress_image(self, img_msg):
        decompressor = pylon.ImageDecompressor()
        decompressor.SetCompressionDescriptor(bytes(img_msg.descriptor))
        try:
            image = decompressor.DecompressImage(bytes(img_msg.imgBuffer))
        except Exception as e:
            print(f"Warning: Failed to decompress image - {e}")
            return np.zeros(FALLBACK_IMAGE_SIZE, dtype=np.uint16)

        return image.Array
