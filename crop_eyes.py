# Crop a photo of a rat to include only the eye.
# The goal of this is to speed up further processing on the eye.
# Command-line input folder_name is folder name where image files are stored. 
# Original images should be saved as filename.<JPG, png, etc.>, and 
# cropped images will be saved in the same folder as filename_cropped.<JPG, png, etc.>.
# Images need to be RGB color (JPG or png is fine), and folder_name should only contain images to be cropped.
# Alpha channel is not necessary (but doesn't hurt).
# Author: Sara Fridovich-Keil
# January 10, 2019
# Modified January 16, 2019


import numpy as np
import matplotlib.image as mpimg
import cv2
import sys
from pathlib import Path

# A Component is a rectangle in an image, designed to enclose reddish regions
class Component:
    # Since python slicing includes the beginning and excludes the end, 
    # Component uses the convention that an object whose actual position 
    # is [row, col] will have corresponding Component [row, row+1, col, col+1]
    def __init__(self, min_row, max_row, min_col, max_col):
        self.min_row = min_row
        self.max_row = max_row
        self.min_col = min_col
        self.max_col = max_col
        
    # Expand this Component to include the point [row, col]
    def merge(self, row, col):
        self.min_row = np.min([self.min_row, row])
        self.max_row = np.max([self.max_row, row])
        self.min_col = np.min([self.min_col, col])
        self.max_col = np.max([self.max_col, col])
    
    # Compute the Manhattan distance between this Component and the point [row, col]
    def l1_distance(self, row, col):
        row_distance = np.max([0, self.min_row - row, row - self.max_row])
        col_distance = np.max([0, self.min_col - col, col - self.max_col])
        return row_distance + col_distance

# Define "reddish" as a class of RGB colors
def is_reddish(color):
    if color[0] < 15:
        return False
    if color[0] < 2*color[1]:
        return False
    if color[0] < 2*color[2]:
        return False
    return True

# Take an RGB image and make anything that isn't reddish black
def find_reddish(image):
    (rows, cols, channels) = image.shape
    for i in range(0,rows):
        for j in range(0,cols):
            color = image[i,j,:]
            if is_reddish(color):
                continue
            else:
                image[i,j,0] = 0
                image[i,j,1] = 0
                image[i,j,2] = 0
    return image


# Crop an RGB image around a Component
def crop_component(img, component, border):
    (rows, cols, channels) = img.shape
    min_row = np.max([component.min_row - border, 0])
    max_row = np.min([component.max_row + border, rows])
    min_col = np.max([component.min_col - border, 0])
    max_col = np.min([component.max_col + border, cols])
    cropped = img[min_row:max_row, min_col:max_col, :]
    return cropped

# Find nearly connected components in a grayscale (scalar-valued) image where background is black
def find_components(gray, min_dist, stride, min_size):
    # min_dist: minimum distance between components before they are merged.
    # stride: controls how much downsampling is done (for speed)
    # min_size: the side length of the smallest allowable component (smaller components are ignored)
    # returns: the Components in a numpy array
    (rows, cols) = gray.shape
    components = []
    for row in range(0,rows,stride):
        for col in range(0, cols,stride):
            if gray[row, col] == 0:
                continue
            close = False
            for component in components:
                if component.l1_distance(row, col) < min_dist:
                    component.merge(row, col)
                    close = True
            if not close:
                components.append(Component(row, row+1, col, col+1))
    components = np.asarray(components)
    # Filter components to not be too small
    big_comps = []
    for component in components:
        if component.max_row - component.min_row < min_size:
            continue
        elif component.max_col - component.min_col < min_size:
            continue
        big_comps.append(component)
    return np.asarray(big_comps)

glob_path = Path(str(sys.argv[1]))
filenames = [str(pp) for pp in glob_path.glob("**/?*.*")]    
for filename in filenames:
    print(filename)

    # Read the image
    original = mpimg.imread(filename)
    reddish = find_reddish(np.copy(original))
    gray = cv2.cvtColor(reddish, cv2.COLOR_BGR2GRAY)
    
    # The eye should be the second highest reddish region in the image 
    components = find_components(gray, min_dist=250, stride=20, min_size=50)
    top_comp = components[0]
    second_comp = components[0]
    for component in components:
        if component.max_row < top_comp.max_row:
            second_comp = top_comp
            top_comp = component
        elif component.max_row < second_comp.max_row:
            second_comp = component
        elif top_comp.max_row == second_comp.max_row:
            second_comp = component
    eye_comp = second_comp
    
    # Crop the image around the eye
    cropped = crop_component(original, eye_comp, 70)

    # Save the cropped image
    mpimg.imsave(filename[0:-4] + "_cropped." + filename[-3:], cropped)




