import math
import os
import argparse
import sys

import cv2
import numpy as np

from util import *


proportion = 1
prop = [proportion]


def parse_args():
    desc = "Tool to quickly click centers of images in dataset and normalize accordingly"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-i", "--input",
                        help="Input folder of images to process")

    parser.add_argument("-o", "--output",
                        help="Output folder of processed images",
                        default="out")

    parser.add_argument("-r", "--resolution", nargs="+", type=int,
                        help="'w h' tuple of desired output resolution")

    parser.add_argument("-d", "--deleted",
                        help="Folder to put deleted images",
                        default="deleted") 
    
    parser.add_argument("-t", "--croptype",
                        help="Type of cropping to do. Currently supported: GIVEN, LARGEST. LARGEST default",
                        default="LARGEST") 

    args = parser.parse_args()
    return args



#global prop, new_resw, new_resh



def on_click(event, x, y, flags, params):


    resw, resh = args.resolution[0], args.resolution[1]

    if event == cv2.EVENT_LBUTTONDOWN:
        h, w = params["img"].shape[0:2]


        cx, cy = int((x/dim[0])*w), int((y/dim[1])*h) #click coords on non-resized image

        print(f"({params['num_img']}/{num_imgs})")
        
        try:
            if args.croptype == "LARGEST":
                crop = crop_largest_bound(img, cx, cy, resw, resh)

            elif args.croptype == "GIVEN":
                new_resw, new_resh = resw * prop[0], resh * prop[0]
                crop = crop_given_resolution(img, cx, cy, new_resw, new_resh)

            cv2.imwrite(f"{args.output}/{fname}", crop)
            cv2.destroyAllWindows()
        except (cv2.error, IndexError):
            print("Crop out of bounds. Retry")

    elif event == cv2.EVENT_MBUTTONDOWN:
        cv2.imwrite(f"{args.deleted}/{fname}", img)
        cv2.destroyAllWindows()

    elif event == cv2.EVENT_MOUSEMOVE:

        new_resw, new_resh = resw * prop[0], resh * prop[0]
        h, w = params["img"].shape[0:2]

        cx, cy = int((x/dim[0])*w), int((y/dim[1])*h)

        drawn = params["resized"].copy()
        cv2.line(drawn, (x,0), (x,3000), (0,20,0), 1)
        cv2.line(drawn, (0,y), (3000,y), (0,20,0), 1)

        rect_width = int((new_resw * params["dim"][0] / w) / 2)
        rect_height = int((new_resh * params["dim"][1] / h) / 2)

        if args.croptype == "GIVEN": cv2.rectangle(drawn, (x - rect_width, y - rect_height), (x + rect_width, y + rect_height), (0, 20, 0), 1)
        cv2.imshow("image", drawn)

    elif event == cv2.EVENT_MOUSEWHEEL and args.croptype == "GIVEN":
        if flags > 0:

            prop[0] = prop[0] + 0.05 * proportion
            print("Res:",round(prop[0], 2))
            
        else:
            prop[0] = prop[0] - 0.05 * proportion
            print("Res:",round(prop[0], 1))

        new_resw, new_resh = resw * prop[0], resh * prop[0]
        h, w = params["img"].shape[0:2]

        cx, cy = int((x/dim[0])*w), int((y/dim[1])*h)

        drawn = params["resized"].copy()
        cv2.line(drawn, (x,0), (x,3000), (0,20,0), 1)
        cv2.line(drawn, (0,y), (3000,y), (0,20,0), 1)

        rect_width = int((new_resw * params["dim"][0] / w) / 2)
        rect_height = int((new_resh * params["dim"][1] / h) / 2)

        if args.croptype == "GIVEN": cv2.rectangle(drawn, (x - rect_width, y - rect_height), (x + rect_width, y + rect_height), (0, 20, 0), 1)
        cv2.imshow("image", drawn)



def get_centers(folder, filename, num_img):



    global dim, img, fname
    fname = filename
    try:
        img = cv2.imread(f"{folder}/{fname}")
        if img is None:
            return

        cv2.namedWindow("image")
        cv2.moveWindow("image", 40,30)

        resized, dim = ResizeWithAspectRatio_dim(img, height=900)
        drawn = resized.copy()
        cv2.namedWindow('image')

        params = {"img": img, "resized": resized, "dim": dim, "fname": fname, "num_img": num_img}
        cv2.setMouseCallback('image', on_click, params)



            
        if cv2.waitKey(0) == ord("q"):
            print("Quitting...")
            sys.exit()

    except Exception as e:
        raise e
    cv2.destroyAllWindows()



def click_centers():

    resw, resh = args.resolution[0], args.resolution[1]

    global num_imgs
    num_imgs = len(os.listdir(args.input))

    new_resw, new_resh = resw * prop[0], resh * prop[0]

    directory = args.input
    deleted = args.deleted
    out = args.output
    if not os.path.exists(out):
        print(f"Did not find the {out} directory. Creating one...")
        os.mkdir(out)
    if not os.path.exists(deleted):
        print(f"Did not find the {deleted} directory. Creating one...")
        os.mkdir(deleted)





    for num_img, fname in enumerate(os.listdir(directory)):
        if fname in os.listdir(out):
            print(f"Already did {fname} ...")
            continue
        if fname in os.listdir(deleted):
            print(f"Already deleted {fname} ...")
            continue
        get_centers(directory, fname, num_img)





def main():
    global args, num_img

    args = parse_args()
    click_centers()



if __name__ == "__main__":
    main()