import argparse
import os
import pdb
from PIL import Image
import imagehash
from collections import defaultdict


def normalize_image(image, new_size):
    """Scales the shortest side of an image to the given new_size and crops the center of the image to a square of 512x512px."""
    width, height = image.size
    if width < height:
        ratio = new_size / width
    else:
        ratio = new_size / height
    image = image.resize((int(width * ratio), int(height * ratio)))
    width, height = image.size
    left = (width - 512) / 2
    top = (height - 512) / 2
    right = (width + 512) / 2
    bottom = (height + 512) / 2
    image = image.crop((left, top, right, bottom))
    return image


def hash_image(image_path, threshold, verbose=False):
    """Takes an image path and a threshold value, hashes the image, and returns the hash value"""
    with Image.open(image_path) as image:
        if verbose:
            print(f"Opened image: {image_path}")
            print(f"Size: {image.size}")
        image = normalize_image(image, 768)
        if verbose:
            print(f"Normalized size: {image.size}")
        hash_val = str(imagehash.phash(image, hash_size=16, hash=ImageHash.Fuzzy()))
        if verbose:
            print(f"Fuzzy hash value: {hash_val}")
        return hash_val


def find_duplicates(image_dir, threshold, verbose=False, verboser=False, debug=False):
    """Find suspected duplicate images in a directory using a fuzzy hash algorithm and the given threshold value"""
    image_hash_dict = defaultdict(list)
    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            image_path = os.path.join(image_dir, filename)
            if verbose or verboser:
                print(f"Processing image: {image_path}")
            if debug:
                pdb.set_trace()
            hash_val = hash_image(image_path, threshold, verbose=verboser)
            image_hash_dict[hash_val].append(filename)

    if verboser:
        print("Final hash dictionary:")
        for hash_val, filenames in image_hash_dict.items():
            print(f"Hash value: {hash_val}")
            print("Filenames:")
            for filename in filenames:
                print(f"\t{filename}")

    suspected_duplicates = []
    for hash_val, filenames in image_hash_dict.items():
        if len(filenames) > 1:
            suspected_duplicates.append(filenames)
    
    if verbose:
        print("Suspected duplicate image sets:")
        for duplicate_set in suspected_duplicates:
            print(duplicate_set)
    
    return suspected_duplicates


def main():
    parser = argparse.ArgumentParser(description="Find suspected duplicate images in a directory using a fuzzy hash algorithm.")
    parser.add_argument("image_dir", help="Path to directory of images")
    parser.add_argument("--threshold", type=int, default=10, help="Hamming distance threshold for fuzzy hashing (suggested range: 1-20)")
    parser.add_argument("--verbose", action="store_true", help="Print more information")
    parser.add_argument("--verboser", action="store_true", help="Print even more information")
    parser.add_argument("--debug", action="store_true", help="Start program in debug mode")
    args = parser.parse_args()

    if args.debug:
        pdb.set_trace()

    suspected_duplicates = find_duplicates(args.image_dir, args.threshold, verbose=args.verbose, verboser
