import argparse
import os
import sys
import imagehash
from PIL import Image

def get_duplicate_images(folder, threshold, verbose):
    if not os.path.exists(folder):
        print("Folder path is invalid!")
        sys.exit()

    image_files = []
    for file in os.listdir(folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_files.append(os.path.join(folder, file))

    hash_dict = {}
    for image_file in image_files:
        with Image.open(image_file) as image:
            hash_value = str(imagehash.average_hash(image))
            if verbose:
                print(f"{image_file} hash value: {hash_value}")
            if hash_value in hash_dict:
                hash_dict[hash_value].append(image_file)
            else:
                hash_dict[hash_value] = [image_file]

    duplicate_images = []
    for hash_value, images in hash_dict.items():
        if len(images) > 1:
            for i in range(len(images)):
                for j in range(i+1, len(images)):
                    diff = imagehash.hexhamming(images[i], images[j])
                    if verbose:
                        print(f"Hamming distance between {images[i]} and {images[j]}: {diff}")
                    if diff <= threshold:
                        duplicate_images.append((images[i], images[j]))

    if not duplicate_images:
        print("No duplicate images found!")
    else:
        print("Duplicate images found:")
        for pair in duplicate_images:
            print(pair)

def main():
    parser = argparse.ArgumentParser(description='Find duplicate images')
    parser.add_argument('folder', help='path to image folder')
    parser.add_argument('--threshold', type=int, default=5,
                        help='threshold for considering images duplicates (recommended range: 3-10)')
    parser.add_argument('--verbose', '-v', action='store_true', help='increase verbosity')
    parser.add_argument('--verboser', '-vv', action='store_true', help='increase verbosity and print comments')

    args = parser.parse_args()

    if args.verboser:
        print("Getting all image files from folder")
        print("Calculating image hashes")
        print("Looking for duplicates using hamming distance")

    get_duplicate_images(args.folder, args.threshold, args.verbose)

if __name__ == '__main__':
    main()
