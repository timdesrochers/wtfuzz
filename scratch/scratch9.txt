import argparse
import os
import sys
import pdb

from PIL import Image
from imagehash import phash
from tqdm import tqdm

# Constants
NORMALIZE_SIZE = 768
ROI_SIZE = 512

def normalize_image(image):
    """
    Normalize the input image based on the shortest side,
    scaling either up or down to NORMALIZE_SIZE on the shortest side.
    """
    width, height = image.size
    if width < height:
        scale = NORMALIZE_SIZE / width
    else:
        scale = NORMALIZE_SIZE / height
    new_size = (int(width * scale), int(height * scale))
    return image.resize(new_size)

def get_roi(image):
    """
    Isolate a ROI of size ROI_SIZE x ROI_SIZE from the center of the input image.
    """
    width, height = image.size
    left = (width - ROI_SIZE) / 2
    top = (height - ROI_SIZE) / 2
    right = (width + ROI_SIZE) / 2
    bottom = (height + ROI_SIZE) / 2
    return image.crop((left, top, right, bottom))

def get_fuzzy_hash(image, threshold):
    """
    Generate a fuzzy hash for the input image using the specified threshold.
    """
    return phash(image, hash_size=8, highfreq_factor=4, threshold=threshold)

def hash_directory(directory, threshold, verbose=False, verboser=False, debug=False):
    """
    Hash all images in the specified directory using the specified threshold.
    Print out a summary table of the filename, original image dimensions, and the fuzzy hash for each image.
    """
    if debug:
        pdb.set_trace()

    hashes = {}
    for filename in tqdm(os.listdir(directory)):
        filepath = os.path.join(directory, filename)
        try:
            image = Image.open(filepath)
        except Exception as e:
            print(f"Error: Could not open {filename}: {str(e)}")
            continue

        # Normalize the image based on the shortest side
        image = normalize_image(image)
        if verbose or verboser:
            print(f"Normalized {filename}: {image.size}")

        # Get the ROI from the center of the normalized image
        image = get_roi(image)
        if verbose or verboser:
            print(f"Extracted ROI from {filename}: {image.size}")

        # Generate the fuzzy hash for the ROI
        image_hash = get_fuzzy_hash(image, threshold)
        if verbose or verboser:
            print(f"Calculated hash for {filename}: {image_hash}")
        
        # Add the hash to the dictionary of hashes
        hashes[filename] = (image.size, image_hash)

    # Print out a summary table of the filename, original image dimensions, and the fuzzy hash
    print("Results:")
    print("Filename\t\tOriginal size\t\tHash")
    for filename, (size, image_hash) in hashes.items():
        print(f"{filename:20}{size}\t{str(image_hash)}")

    # Find suspected duplicates based on fuzzy hash
    duplicates = {}
    for filename, (size, image_hash) in hashes.items():
        for filename2, (size2, image_hash2) in hashes.items():
            if filename != filename2 and (image_hash - image_hash2) <= threshold:
                if filename not in duplicates:
                    duplicates[filename] = []
                duplicates[filename].append(filename2)

    # Print out any suspected duplicates
    if duplicates:
        print("\
