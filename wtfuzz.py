import os
import sys
import argparse
import pdb
from PIL import Image
import imagehash

def normalize(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        if min(width, height) != 768:
            if width > height:
                ratio = 768 / height
                new_size = (int(width * ratio), 768)
            else:
                ratio = 768 / width
                new_size = (768, int(height * ratio))
            img = img.resize(new_size, Image.ANTIALIAS)
        center_x, center_y = img.size[0] // 2, img.size[1] // 2
        roi = img.crop((center_x - 256, center_y - 256, center_x + 256, center_y + 256))
        return roi

def get_image_hash(image_path, hashfunc=imagehash.phash, hash_size=16):
    image = normalize(image_path)
    hash_value = hashfunc(image, hash_size=hash_size)
    print(f"{image_path} -- hash: {hash_value}")
    return hash_value

def find_duplicates(image_dir, threshold, verbose, verboser, debug):
    image_hashes = {}
    for root, dirs, files in os.walk(image_dir):
        for name in files:
            if name.endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(root, name)
                hash_value = get_image_hash(path)
                if hash_value in image_hashes:
                    image_hashes[hash_value].append(path)
                else:
                    image_hashes[hash_value] = [path]
    if verbose or verboser:
        print("Summary Table")
        print("{:<40} {:<20} {}".format('File', 'Dimensions', 'Hash'))
    for key in image_hashes:
        if len(image_hashes[key]) > 1:
            if verboser:
                print(f"Potential duplicates -- hash: {key}")
                for path in image_hashes[key]:
                    print(f"\t{path}")
            else:
                if verbose:
                    print(f"{image_hashes[key]}")
                else:
                    print(f"Potential duplicates found for hash {key}:")
                    for path in image_hashes[key]:
                        print(f"\t{path}")
                if debug:
                    pdb.run("normalize(path).show()")

def main():
    parser = argparse.ArgumentParser(description='Find duplicate images in a directory.')
    parser.add_argument('directory', type=str, help='Directory of images to check for duplicates')
    parser.add_argument('-t', '--threshold', type=int, default=10,
                        help='Threshold value to set the hamming distance used in the fuzzy hashing')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')
    parser.add_argument('-vv', '--verboser', action='store_true',
                        help='Greatly increase output verbosity')
    parser.add_argument('--debug', action='store_true',
                        help='Enter pdb interactive debugger')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"{args.directory} is not a directory")
        sys.exit(1)

    if args.threshold < 1 or args.threshold > 20:
        print("Threshold value should be between 1 and 20.")
        sys.exit(1)

    find_duplicates(args.directory, args.threshold, args.verbose, args.verboser, args.debug)

if __name__ == '__main__':
    main()
