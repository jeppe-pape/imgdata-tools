import math
import os
import json
import shutil

import cv2
import numpy as np
import matplotlib.pyplot as plt

import numpy as np

# Wrapping function
def bounds_checked_slice(arr):
    return SliceBoundsChecker(arr)

# Wrapper that checks that indexing slices are within bounds of the array
class SliceBoundsChecker:

    def __init__(self, arr):
        self._arr = np.asarray(arr)

    def __getitem__(self, args):
        # Slice bounds checking
        self._check_slice_bounds(args)
        return self._arr.__getitem__(args)

    def __setitem__(self, args, value):
        # Slice bounds checking
        self._check_slice_bounds(args)
        return self._arr.__setitem__(args, value)

    # Check slices in the arguments are within bounds
    def _check_slice_bounds(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        # Iterate through indexing arguments
        arr_dim = 0
        i_arg = 0
        for i_arg, arg in enumerate(args):
            if isinstance(arg, slice):
                self._check_slice(arg, arr_dim)
                arr_dim += 1
            elif arg is Ellipsis:
                break
            elif arg is np.newaxis:
                pass
            else:
                arr_dim += 1
        # Go backwards from end after ellipsis if necessary
        arr_dim = -1
        for arg in args[:i_arg:-1]:
            if isinstance(arg, slice):
                self._check_slice(arg, arr_dim)
                arr_dim -= 1
            elif arg is Ellipsis:
                raise IndexError("an index can only have a single ellipsis ('...')")
            elif arg is np.newaxis:
                pass
            else:
                arr_dim -= 1

    # Check a single slice
    def _check_slice(self, slice, axis):
        size = self._arr.shape[axis]
        start = slice.start
        stop = slice.stop
        step = slice.step if slice.step is not None else 1
        if step == 0:
            raise ValueError("slice step cannot be zero")
        bad_slice = False
        if start is not None:
            start = start if start >= 0 else start + size
            bad_slice |= start < 0 or start >= size
        else:
            start = 0 if step > 0 else size - 1
        if stop is not None:
            stop = stop if stop >= 0 else stop + size
            bad_slice |= (stop < 0 or stop > size) if step > 0 else (stop < 0 or stop >= size)
        else:
            stop = size if step > 0 else -1
        if bad_slice:
            raise IndexError("slice {}:{}:{} is out of bounds for axis {} with size {}".format(
                slice.start if slice.start is not None else '',
                slice.stop if slice.stop is not None else '',
                slice.step if slice.step is not None else '',
                axis % self._arr.ndim, size))


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

        crop = bounds_checked_slice(image)[cy-(int(min_width*resh/resw)):cy+(int(min_width*resh/resw)), cx-min_width:cx+min_width]

    else:
        crop = bounds_checked_slice(image)[cy-min_height:cy+min_height, cx-(int(min_height*resw/resh)):cx+(int(min_height*resw/resh))]
    return crop

def crop_given_resolution(image, cx, cy, resw, resh):

    w, h = int(resw / 2), int(resh / 2)
    crop = bounds_checked_slice(image)[cy-h: cy+h, cx-w: cx+w]
    return crop