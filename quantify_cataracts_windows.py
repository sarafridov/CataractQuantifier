# Quantify rat cataracts from photographs, with shading as follows:
# Red: lens (cataract or clear)
# Green: eye outside lens
# Blue (optional): 4 marks around border of cataract
# Black (optional): 4 marks around border of eye
# Command-line input is folder name where files are stored. 
# Original images should be saved as filename.png, and 
# shaded images should be saved as filename.shaded.png.
# Output for all images in the input folder will be saved 
# in a csv file with the same name as the folder (but not inside the folder).
# Tips: Crop the images to only show the eye, so that the code runs faster. 
# Images need to be RGB color and saved in png format. Alpha channel is not necessary (but doesn't hurt).
# Author: Sara Fridovich-Keil
# January 30, 2018
# Modified February 1, 2018


import numpy as np
import matplotlib.image as mpimg
import cv2
import sys
import glob
import csv

# Compute average RGB color of an RGB image, ignoring white pixels
def mean_color(image):
    (rows, cols, channels) = image.shape
    rsum = 0.0
    gsum = 0.0
    bsum = 0.0
    count = 0
    white = [1,1,1]
    for i in range(0,rows):
        for j in range(0,cols):
            if (compare_colors(image[i,j,:], white)==True):
                continue
            rsum += image[i,j,0]
            gsum += image[i,j,1]
            bsum += image[i,j,2]
            count += 1
    return [rsum/count, gsum/count, bsum/count]

# Given a color and two images, set all pixels in the second image to white if their corresponding pixels in the first image are not that color
def crop_color(template, output, color):
    (rows, cols, channels) = template.shape
    for i in range(0,rows):
        for j in range(0,cols):
            cur_col = template[i,j,:]
            if (compare_colors(cur_col, color)==False):
                output[i,j,0] = 1
                output[i,j,1] = 1
                output[i,j,2] = 1
    return output

# Compare two colors and determine if they are close enough to be considered equal
def compare_colors(color_1, color_2):
    threshold = 0.2
    if (np.abs(color_1[0] - color_2[0]) > threshold):
        return False
    if (np.abs(color_1[1] - color_2[1]) > threshold):
        return False
    if (np.abs(color_1[2] - color_2[2]) > threshold):
        return False
    return True

# Given a color and two images, make a grayscale black/white image with black when corresponding pixels in the first image are not that color
def threshold_color(template, color):
    (rows, cols, channels) = template.shape
    output = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    for i in range(0,rows):
        for j in range(0,cols):
            cur_col = template[i,j,:]
            if (compare_colors(cur_col, color)==False):
                output[i,j] = 0
            else:
                output[i,j] = 1
    return output

# Fit an ellipse to a black and white image with endpoints marked
def fit_ellipse(img):
    img,contours,hierarchy = cv2.findContours(img, 1, 2)
    cv2.drawContours(img, contours, -1, (1,0,0), 3)
    cnt = [item for sublist in contours for item in sublist] # Flatten the contours list
    # Fit an ellipse
    ellipse = cv2.fitEllipse(np.asarray(cnt)) # Ellipse is a rotated rectangle with the ellipse inscribed
    cv2.ellipse(img,ellipse,(1,0,0),1)
    # Record the area of the ellipse
    area = np.pi * ellipse[1][0] * ellipse[1][1] / 4.0
    return area

filenames = glob.glob(sys.argv[1] + "\*.shaded.png")
with open(sys.argv[1] + ".csv", "w") as csvfile:
    # Write column headers
    writer = csv.writer(csvfile, delimiter = ",")
    writer.writerow(["File Name", "Mean Lens Brightness", "Mean Sclera Brightness", 
        "Lens/Sclera Brightness Ratio", "Cataract Area", "Total Eye Area", "Cataract/Eye Area Ratio"])

    for filename in filenames:
        originalname = filename[0:-10] + "png"

        # Read the images
        shaded = mpimg.imread(filename)
        original = mpimg.imread(originalname)

        # Make a copy of the original image, with only the part shaded in red left not white
        red = [1,0,0]
        red_crop = original.copy()
        red_crop = crop_color(shaded, red_crop, red)

        # Make a copy of the original image, with only the part shaded in green left not white
        green = [0,1,0]
        green_crop = original.copy()
        green_crop = crop_color(shaded, green_crop, green)

        # Make a copy of the original image, with only the part shaded in blue thresholded to 1, and fit an ellipse
        blue = [0,0,1]
        blue_crop = threshold_color(shaded, blue)
        if np.max(blue_crop) >= 1:
            ret,blue_thresh = cv2.threshold(blue_crop,0,255,cv2.THRESH_BINARY)
            blue_thresh = np.uint8(blue_thresh)
            blue_area = fit_ellipse(blue_thresh)

        # Make a copy of the original image, with only the part shaded in black thresholded to 1, and fit an ellipse
        black = [0,0,0]
        black_crop = threshold_color(shaded, black)
        if np.max(black_crop) >= 1:
            ret,black_thresh = cv2.threshold(black_crop,0,255,cv2.THRESH_BINARY)
            black_thresh = np.uint8(black_thresh)
            black_area = fit_ellipse(black_thresh)

        mean_red_color = np.mean(mean_color(red_crop))
        mean_green_color = np.mean(mean_color(green_crop))
        writer = csv.writer(csvfile, delimiter = ",")
        if np.max(blue_crop) >= 1 and np.max(black_crop) >= 1:
            writer.writerow([originalname.split("\\")[1], mean_red_color, 
                mean_green_color, mean_red_color/mean_green_color, blue_area, black_area, blue_area/black_area])
        else:
            writer.writerow([originalname.split("\\")[1], mean_red_color, 
                mean_green_color, mean_red_color/mean_green_color])

