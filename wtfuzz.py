import os
import argparse
import logging
import pdb
from PIL import Image
import imagehash


def normalize_image(image):
    width, height = image.size
    short_side = min(width, height)
    left = (width - short_side) / 2
    top = (height - short_side) / 2
    right = (width + short_side) / 2
    bottom = (height + short_side) / 2
    roi = image.crop((left, top, right, bottom)).resize((512, 512))
    return roi


def hash_image(filepath, threshold):
    image = Image.open(filepath).convert('RGB')
    normalized_image = normalize_image(image)
    hash_value = imagehash.phash(normalized_image, hash_size=16)
    return hash_value


def main():
    parser = argparse.ArgumentParser(description='Fuzzy image hashing program')
    parser.add_argument('dir', help='directory to search for images')
    parser.add_argument('--threshold', type=int, default=10, help='maximum hamming distance to consider duplicates')
    parser.add_argument('--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('--verboser', action='store_true', help='increase output verbosity with comments')
    parser.add_argument('--debug', action='store_true', help='run in debug mode')
    args = parser.parse_args()
    
    if args.debug:
        pdb.set_trace()
    
    logging_level = logging.DEBUG if args.verbose or args.verboser else logging.INFO
    logging.basicConfig(format='%(message)s', level=logging_level)
    
    hash_dict = {}
    for root, dirs, files in os.walk(args.dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                hash_value = hash_image(filepath, args.threshold)
            except OSError:
                logging.warning(f"Could not open {filepath}")
                continue
            
            if hash_value in hash_dict:
                duplicate_filepath = hash_dict[hash_value]
                if args.verboser:
                    logging.info(f"{filepath} has the same hash value as {duplicate_filepath}")
                if args.verbose:
                    logging.info(f"Possible duplicate: {filepath} and {duplicate_filepath}")
            else:
                hash_dict[hash_value] = filepath
    
    if args.verboser:
        logging.info('Fuzzy hash values:')
        for hash_value, filepath in hash_dict.items():
            logging.info(f"{hash_value}: {filepath}")
    
    if args.verbose or args.verboser:
        logging.info('Suspected duplicates:')
    for hash_value, filepath in hash_dict.items():
        suspected_files = [v for k, v in hash_dict.items() if k - hash_value <= args.threshold and k != hash_value]
        if len(suspected_files) > 0:
            if args.verboser:
                logging.info(f"{filepath}: {hash_value}")
            if args.verbose or args.verboser:
                logging.info(f"Suspected duplicates of {filepath}: {', '.join(suspected_files)}")


if __name__ == '__main__':
    main()
