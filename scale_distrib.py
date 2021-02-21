import json
import os
import shutil
import math
import argparse

import cv2


from util import *



def parse_args():
    desc = "Tool to quickly click centers of images in dataset and normalize accordingly"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-i", "--input",
                        help="Input folder of images to process")

    parser.add_argument("-o", "--output",
                        help="Base name for output folders. Will be appended 'xN' where N number of upscales needed")

    parser.add_argument("-w", "--width", type=int,
                        help="desired width of images")

    parser.add_argument("--max_upscale", type=int,
                        help="Maximum scale factor to make a folder for. Default 4",
                        default=4)
    
    parser.add_argument("--pre_resize",
                        help="Whether to resize given image to be ready for upscale (ex. img in x4 folder will be resized to 1/4 of desired res)",
                        action="store_true") 

    parser.add_argument("--height", type=int,
                        help="Pass if preresizing. Desired width of correctly upscaled image",) 

    args = parser.parse_args()
    return args


def distribute_to_upscale(folder, desired_width, max_upscale=4, pre_resize=False, desired_height=None, out_name=None):
    print(f"Distributing {folder} to desired folders...")
    

    assert max_upscale in (0, 2, 4, 6, 8, 10)

    upscales = list(range(0, max_upscale+1, 2))
    upscales[0] = 1
    # upscales = [1, 2, 4, 6, 8, ...]
    score = {scale: 0 for scale in upscales}

    if pre_resize:
        assert desired_height is not None

        assert all(math.modf(desired_width / scale)[0] == 0 for scale in upscales), "width not divisible by all upscales"
        assert all(math.modf(desired_height / scale)[0] == 0 for scale in upscales), "height not divisible by all upscales"

    total = len(os.listdir(folder))

    for n, fname in enumerate(os.listdir(folder)):


        string = f"Total: {round((n/total) * 100, 1)}%     "
        for s in score:
            string += f"x{s}:{score[s]}     "
        print(string, end="\r")


        path = os.path.join(folder, fname)

        for scale in upscales:

            if out_name is None:
                folder_name = f"{folder}_x{scale}"
            else:
                folder_name = f"{out_name}_x{scale}"

            if not os.path.exists(folder_name): os.mkdir(folder_name)

            if get_image_size(path)[0] >= (desired_width / scale) * 0.8:

                if pre_resize:
                    img = cv2.imread(path)
                    img = cv2.resize(img, (int(desired_width / scale), int(desired_height / scale)), interpolation = cv2.INTER_CUBIC)
                    cv2.imwrite(os.path.join(folder_name,fname), img)
                else:
                    shutil.copyfile(path, os.path.join(folder_name,fname))
                score[scale] += 1
                break

    print(f"\nCompleted folder distribution")




def main():

    global args

    args = parse_args()
    distribute_to_upscale(args.input, args.width,
                        max_upscale=args.max_upscale,
                        pre_resize=args.pre_resize,
                        desired_height=args.height,
                        out_name=args.output)



if __name__ == "__main__":
    main()