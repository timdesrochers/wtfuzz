import argparse
import os
import pdb
from PIL import Image
import imagehash

def get_fuzzy_hash(image, threshold):
    # calculate the pHash for the image
    hash = imagehash.phash(image)
    return hash

def get_roi(image, debug):
    w, h = image.size
    size = min(w, h)
    h_offset = (h - size) // 2
    w_offset = (w - size) // 2
    roi = image.crop((w_offset, h_offset, w_offset + size, h_offset + size))
    roi = roi.resize((512, 512))
    print(f'19.ROI image dimensions: {roi.size}')
    if debug:
        roi.show()
        pdb.set_trace()
    return roi


def normalize_image(image, debug):
    w, h = image.size
#    scale_factor = 768 / min(h, w)
#    new_w = int(w * scale_factor)
#    new_h = int(h * scale_factor)
    if h < w:
        new_h = 768
        new_w = int(w * (new_h / h))
    else:
        new_w = 768
        new_h = int(h * (new_w / w))
    image = image.resize((new_w, new_h), Image.ANTIALIAS)
    print(f'32.Normalized image dimensions: {image.size}')
    if debug:
        image.show()
        pdb.set_trace()
    return image

def process_image(image_path, threshold, debug):
    try:
        image = Image.open(image_path)
    except IOError:
        print(f'{image_path} is not an image file. Skipping...')
        return
    print(f'Processing image: {image_path}')
    print(f'41.Original image dimensions: {image.size}')

    image = normalize_image(image, debug)
    print(f'44.Normalized image dimensions: {image.size}')

    roi = get_roi(image, debug)
    print(f'ROI image dimensions: {roi.size}')
    if debug:
        pdb.set_trace()

    fuzzy_hash = get_fuzzy_hash(roi, threshold)
    print(f'Fuzzy hash: {fuzzy_hash}')
    return image_path, fuzzy_hash

def process_images(image_dir, threshold, debug):
#   filenames = os.listdir(image_dir)
    image_hashes = {}
    for filename in os.listdir(image_dir):
        image_path = os.path.join(image_dir, filename)
        if os.path.isfile(image_path):
            try:
                image_path, fuzzy_hash = process_image(image_path, threshold, debug)
            except TypeError:
                print(f'{image_path} seems not to be an image file. Skipping...')
                return
            image_hashes[image_path] = fuzzy_hash
    
    print('\nSummary:')
    print('Filename\t\tOriginal Dimensions\t\tFuzzy Hash')
    for image_path, fuzzy_hash in image_hashes.items():
        image = Image.open(image_path)
        print(f'{image_path}\t\t{image.size}\t\t{fuzzy_hash}')

    print('\nDuplicate Images:')
    for image1, hash1 in image_hashes.items():
        for image2, hash2 in image_hashes.items():
            hamming_distance = hash1 - hash2
            if hamming_distance <= threshold and image1 != image2:
                print(f'{image1} and {image2} are suspected duplicates with hamming distance of {hamming_distance}')

def main():
    parser = argparse.ArgumentParser(description='Process a directory of images and generate fuzzy hashes.')
    parser.add_argument('image_dir', help='Directory of images to process')
    parser.add_argument('--threshold', type=int, default=20, help='Hamming distance threshold for fuzzy hashing')
    parser.add_argument('--debug', action='store_true', help='Enable debugging with pdb')
    args = parser.parse_args()

    process_images(args.image_dir, args.threshold, args.debug)

if __name__ == '__main__':
    main()

