
# Converting from our GT format (modified YOLO format, where object_id added):
# [Class ID, Object ID, x, y, w, h] (relative coordinates)
# to PASCAL VOC format that Carchuno/mAP accepts:
# [class_id, x1, y1, x2, y2] (absolute coordinates)

# Note: x and y are center position of bbox,
# x1 and y1 are the top-left corner bbox,
# x2 and y2 are the bottom-right corner of bbox
# w is width, h is height

# We defined "all" object classes as all the classes that exist in ground truth.
# Or we can input specific class_id to filter.

# load libraries
import glob
import numpy as np
from tqdm import tqdm
import argparse
import re
import pdb # for debugging


def normalize(value, minValue, maxValue, a, b):
    return (value - minValue) / (maxValue - minValue) * (b - a) + a # normalize to [a, b] for drawing


# sort the string in a natural way. E.g., "0" -> "2" -> "10" instead of "0" -> "10" -> "2"
def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)] 
    return sorted(l, key=alphanum_key)


# inputs for the command
def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Inputs for data conversion')
    parser.add_argument("--input_dir_gt", help="Enter the ground truth input path", type=str)
    parser.add_argument("--output_dir_gt", help="Enter the converted ground truth output path", type=str)
    parser.add_argument("--class_id_filter", help="Select either class ID to filter or \"all\" classes", type=str)
    parser.add_argument("--img_w", help="Enter the width in pixel of video image frame", type=int)
    parser.add_argument("--img_h", help="Enter the height in pixel of video image frame", type=int)
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_args()
    input_dir_gt = args.input_dir_gt
    output_dir_gt = args.output_dir_gt
    class_id_filter = args.class_id_filter
    img_w = args.img_w
    img_h = args.img_h

    # ----------------------------------------------------------------
    # Convert GT files
    # ----------------------------------------------------------------
    print("Converting GT files to mAP format ...")
    alltxt_gt = natural_sort(glob.glob(f"{input_dir_gt}/*.txt"))
    for txt in tqdm(alltxt_gt):
        txt = txt.replace("\\","/") # some system have back slash instead of forward slash
        txt_name = txt.split("/")[-1]
        with open(f"{output_dir_gt}/{txt_name}", 'w') as output_file:
            class_id, object_id, x, y, w, h = np.genfromtxt(txt, unpack=True)

            # conversion of bbox
            x = normalize(x, 0, 1, 0, img_w)
            y = normalize(y, 0, 1, 0, img_h)
            w = normalize(w, 0, 1, 0, img_w)
            h = normalize(h, 0, 1, 0, img_h)

            # x1 y1 is top-left, x2 y2 is bottom-right corner of bbox
            x1 = x - w / 2
            y1 = y - h / 2
            x2 = x + w / 2
            y2 = y + h / 2

            # if class filter is all object classes, don't filter
            if class_id_filter != "all":
                data = np.array([class_id, x1, y1, x2, y2]).T
                if data.ndim > 1:
                    data = data[data[:,0]==int(class_id_filter)] # filtering by the class id
                else:
                    # if the data is 1-dim, don't save into GT
                    if data[1] != int(class_id_filter):
                        continue
                class_id, x1, y1, x2, y2 = data.T

            # save into GT file
            np.savetxt(output_file, np.column_stack(\
                (class_id, x1, y1, x2, y2)\
                    ), delimiter=' ', fmt="%d %s %s %s %s")
