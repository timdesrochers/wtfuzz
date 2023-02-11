import argparse
import os
from PIL import Image
import imagehash


def fuzzy_hash(filepath, hash_size=8):
    with Image.open(filepath) as image:
        image_hash = imagehash.phash(image, hash_size=hash_size)
        return str(image_hash)


def process_images(images_path, threshold, hash_size, verbose, verboser):
    hashes = {}
    duplicates = []

    for filename in os.listdir(images_path):
        filepath = os.path.join(images_path, filename)
        if os.path.isfile(filepath):
            try:
                image_hash = fuzzy_hash(filepath, hash_size=hash_size)
            except OSError:
                print(f"Error reading {filepath}")
                continue

            if verbose:
                print(f"Hashed {filename} as {image_hash}")

            for existing_filename, existing_image_hash in hashes.items():
                hamming_distance = imagehash.hex_to_hash(existing_image_hash) - imagehash.hex_to_hash(image_hash)
                if hamming_distance <= threshold:
                    if verboser:
                        print(f"{filename} is a suspected duplicate of {existing_filename} (hamming distance: {hamming_distance})")
                    else:
                        print(f"{filename} is a suspected duplicate of {existing_filename}")
                    duplicates.append((filename, existing_filename))
                    break

            hashes[filename] = image_hash

    return duplicates


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find fuzzy duplicates in a directory of images')
    parser.add_argument('images_path', help='Path to directory containing images')
    parser.add_argument('--hash-size', type=int, default=8, help='Hash size for image hashing (default: 8)')
    parser.add_argument('--threshold', type=int, default=6, help='Maximum acceptable Hamming distance (default: 6, valid range: 0-64)')
    parser.add_argument('--verbose', action='store_true', help='Verbose mode, print hashed filename')
    parser.add_argument('--verboser', action='store_true', help='Even more verbose mode, print explanatory comments')
    args = parser.parse_args()

    if not 0 <= args.threshold <= 64:
        parser.error('--threshold must be between 0 and 64')

    if args.verboser:
        for arg in vars(args):
            print(f"{arg}: {getattr(args, arg)}")
        print("Finding fuzzy duplicates in directory", args.images_path)
        print("Using hash size:", args.hash_size)
        print(f"Threshold set at {args.threshold} - images with a Hamming distance lower than this value will be considered as duplicates")

    duplicates = process_images(args.images_path, args.threshold, args.hash_size, args.verbose, args.verboser)

    if duplicates:
        print("Suspected duplicates:")
        for pair in duplicates:
            print(pair[0], pair[1])
    else:
        print("No duplicates found.")
