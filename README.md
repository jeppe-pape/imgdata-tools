# imgdata-tools
This is a small set of simple cv2 tools for quick manual centering and normalizing of images - intended for reasonably sized image datasets

# Installation
This toolset is dependent on:
- python - https://www.python.org/downloads/
- cv2 - https://pypi.org/project/opencv-python/

If you have python installed, get cv2 with pip: ```pip install opencv-python``` and you should be ready to go!

# Basic Use

## Centering:
```
python click_centers.py -i 'path/to/input/folder' -r 'resolution_width resolution_height'
```
Instructions: Click on the center of your ROI of the image that pops up. The centered image will appear in your "out" folder. Continue until folder is empty. Simple.
Has two modes:

```--croptype LARGEST``` (default), which will crop the biggest possible image with your chosen point as center. 

```--croptype GIVEN```, which will let you change your crop width dynamically with the mouse wheel

If you want to not use a given image, press middle mouse button, and it will copy the (uncropped) image to the ```--deleted``` folder (default "deleted")

## Normalizing:
```
python scale_distrib.py -i 'path/to/input/folder -w 'desired_width'
```
This is a pretty specific tool intended for use with AI upscaling software. Will take all images of the input folder (typically the output folder of click_centers.py) and distribute them into different subfolders based on their resolution.

Example: input folder 'cats' contains 'cat_image001.jpg' which is 1750x1024. My desired width is 1920 so cat_image will be put in the 'cats_2x' folder. Why? Because it will need to be upscaled 2x before being shrunk to my desired width.

If you want to resize the images so that they will be the exact desired resolution after upscaling, pass the ```--pre_resize``` flag along with ```--height 'desired height'```. 

  
