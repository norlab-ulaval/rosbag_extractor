import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.interpolate import UnivariateSpline

#######################################################
PATH_IMGS = "/home/norlab/ros/bags/out/camera_left"
NUMBER_IMAGES = 1000
MIN_EXPOSURE_TIME = 0.02
MAX_EXPOSURE_TIME = 50
SKIP_IMAGES = 5
#########################################################

def load_images_from_folder(folder, nb_images, skip_images=1):
    images = []
    means = []
    filenames = sorted(os.listdir(folder))  # Assuming filenames are in order of exposure

    print("Loading images...")
    for filename in tqdm(filenames[:nb_images:skip_images]):
        img = cv2.imread(os.path.join(folder, filename))
        if img is not None:
            images.append(img)
            means.append(np.mean(img))
    
    # Find first idx
    diff_means = np.abs(np.diff(means))
    idx = np.argmax(diff_means)+1

    return images, idx

def create_exposure_time_logspace(min_exposure_time, max_exposure_time, number_values, skip_values=1):
    print("Creating exposure time logspace...")
    min_log = np.log(min_exposure_time)
    max_log = np.log(max_exposure_time)
    values_linspace = np.linspace(min_log, max_log, number_values)
    values_logspace = np.exp(values_linspace)
    values = (values_logspace * 10000).astype("int") / 10000
    return values[::skip_values]

def compute_icrf(images, first_idx, exposure_times):

    print("Computing CRF...")
    images = images[first_idx:] + images[:first_idx]
    exposure_times = np.array(exposure_times, dtype=np.float32)

    # Estimate the CRF using Debevec method
    calibrate = cv2.createCalibrateDebevec()
    icrf = calibrate.process(images, exposure_times)

    return icrf

def visualize_crf(icrf):
    print("Visualizing CRF...")
    icrf = icrf.squeeze()  # Remove single-dimensional entries
    plt.figure(figsize=(10, 5))
    for channel, color in zip(range(3), ['red', 'green', 'blue']):
        plt.plot(np.arange(256), np.log(icrf[:, channel]), color=color, label=f'{color} channel')
    plt.xlabel('Pixel Value')
    plt.ylabel('Calibrated Intensity')
    plt.title('Inverse Camera Response Function (CRF)')
    plt.grid(True)

    print("Visualizing inverse CRF...")
    plt.figure(figsize=(10, 5))
    for channel, color in zip(range(3), ['red', 'green', 'blue']):
        plt.plot(icrf[:, channel], np.arange(256), color=color, label=f'{color} channel')
    plt.xlabel('Calibrated Intensity')
    plt.ylabel('Pixel Value')
    plt.title('Camera Response Function (CRF)')
    plt.grid(True)
    # plt.show()

    # Compute the derivative of ln(icrf)
    print("Computing derivative of ln(icrf)...")
    ln_icrf = np.log(icrf)
    derivative_ln_icrf = np.gradient(ln_icrf, axis=0)

    # Plot the derivative of ln(icrf)
    plt.figure(figsize=(10, 5))
    for channel, color in zip(range(3), ['red', 'green', 'blue']):
        plt.plot(np.arange(256), derivative_ln_icrf[:, channel], color=color, label=f'{color} channel')
    plt.xlabel('Pixel Value')
    plt.ylabel('Derivative of ln(Calibrated Intensity)')
    plt.title('Derivative of ln(Inverse Camera Response Function)')
    plt.grid(True)
    plt.legend()
    plt.show()

def save_calib(filename, icrf):
    print(f"Saving CRF to {filename}...")
    with open(filename, 'w') as f:
        f.write(' '.join(map(str, icrf)))

if __name__ == "__main__":
    # Folder containing images
    image_folder = "/home/norlab/ros/bags/out/camera_left"

    # Compute the CRF
    images, first_idx = load_images_from_folder(image_folder, NUMBER_IMAGES, SKIP_IMAGES)
    exposures = create_exposure_time_logspace(MIN_EXPOSURE_TIME, MAX_EXPOSURE_TIME, NUMBER_IMAGES, SKIP_IMAGES)
    icrf = compute_icrf(images, first_idx, exposures)
    visualize_crf(icrf)

    icrf = np.mean(icrf.squeeze(), axis=1)
    save_calib("crf.txt", icrf)

