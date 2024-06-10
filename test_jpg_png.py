import cv2
import numpy as np

img_jpg = cv2.imread("/home/olivier_g/Desktop/tmp/export/camera_left/16.0/1695833463511869952.jp2", cv2.IMREAD_ANYDEPTH)
# print(f"Max: {np.max(img_jpg)}")
img_png = cv2.imread("/home/olivier_g/Desktop/tmp/export/camera_leftpng/16.0/1695833463511869952.png", cv2.IMREAD_ANYDEPTH)

if np.all(img_jpg == img_png):
    print("Images are equal.")
    
print(np.count_nonzero(img_jpg == img_png))
print(np.mean(img_jpg - img_png))
print(img_jpg.shape[0]*img_jpg.shape[1])