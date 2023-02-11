# wtfuzz
an attempt at fuzzy image hashing

`wtfuzz` will accept a directory of images as an argument. After normalizing the imageset, it will isolate a 512x512px crop of the center of the image and use `phash` to attempt to identify similar images. 

The sensitivity of the hash can be adjusted with the `--threshold` flag, which adjusts the hamming value. 10 is the default and a decent place to start.

## Future plans
- Add flag to adjust offset of ROI (region of interest) crop for hashing.
- File operations to rename or move suspected duplicates.
- "Diffusion genealogy" -- but more on that later.
