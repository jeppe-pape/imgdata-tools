import math
import os
import json
import shutil

import cv2
import numpy as np
import matplotlib.pyplot as plt

# open output file for writing
def write_list(path, j_list):
    with open(path, 'w') as filehandle:
        json.dump(j_list, filehandle)


# open output file for reading
def load_list(path):
    with open(path, 'r') as filehandle:
        j_list = json.load(filehandle)
        return j_list

import struct
import imghdr

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

def ResizeWithAspectRatio_dim(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return (cv2.resize(image, dim, interpolation=inter), dim)

def crop_largest_bound(image, cx, cy, resw, resh):

    min_width = min(cx, (image.shape[1] - cx))
    min_height = min(cy, (image.shape[0] - cy))



    if min_width / resw < min_height / resh: # if width bound closest

        crop = image[cy-(int(min_width*resh/resw)):cy+(int(min_width*resh/resw)), cx-min_width:cx+min_width]

    else:
        crop = image[cy-min_height:cy+min_height, cx-(int(min_height*resw/resh)):cx+(int(min_height*resw/resh))]
    return crop

def crop_given_resolution(image, cx, cy, resw, resh):

    w, h = int(resw / 2), int(resh / 2)
    crop = image[cy-h: cy+h, cx-w: cx+w]
    return crop