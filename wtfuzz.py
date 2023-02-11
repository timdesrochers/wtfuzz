import os
import argparse
from PIL import Image
import imagehash
import pdb

def normalize_and_hash_images(image_directory, debug=False, verbose=False):
    hashes = {}
    for filename in os.listdir(image_directory):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            image_path = os.path.join(image_directory, filename)
            with Image.open(image_path) as im:
                if verbose:
                    print(f"Processing image: {filename}")
                    print(f"Image size: {im.size}")
                width, height = im.size
                if width >= height:
                    left = (width - height) // 2
                    right = left + height
                    box = (left, 0, right, height)
                else:
                    top = (height - width) // 2
                    bottom = top + width
                    box = (0, top, width, bottom)
                im = im.crop(box)
                im = im.resize((512, 512))
                if debug:
                    pdb.set_trace()
                    im.show()
                phash = str(imagehash.phash(im))
                if phash in hashes:
                    hashes[phash].append(filename)
                else:
                    hashes[phash] = [filename]
    return hashes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process and hash a directory of images')
    parser.add_argument('directory', type=str, help='path to the image directory')
    parser.add_argument('--debug', action='store_true', help='enable debugging mode')
    parser.add_argument('--verbose', action='store_true', help='enable verbose output')
    args = parser.parse_args()
    normalize_and_hash_images(args.directory, args.debug, args.verbose)
