
# Converting from our GT format (modified YOLO format, where object_id added):
# [Class ID, Object ID, x, y, w, h] (relative coordinates)
# to MOT challenge format that cheind/py-motmetrics accepts:
# [Frame Index, Object ID, x1, y1, w, h, Confidence, 3D x, 3D y, 3D z] (absolute coordinates)

# Note: x and y are center position of bbox,
# x1 and y1 are the top-left corner bbox,
# x2 and y2 are the bottom-right corner of bbox
# w is width, h is height

# MOT challenge format does not distinguish different class_id, so we will be the one to filter.
# We defined "all" object classes as all the classes that exist in ground truth and object_id range
# indifferent to class_id.
# Or we can input specific class_id to filter.

# load libraries
import glob
import numpy as np
from tqdm import tqdm
import argparse
import re
import os
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
    parser = argparse.ArgumentParser(description='Inputs for data conversion')
    parser.add_argument("--input_dir_gt", help="Enter the ground truth input directory path", type=str)
    parser.add_argument("--output_dir_gt", help="Enter the converted ground truth output directory path", type=str)
    parser.add_argument("--class_id_filter", help="Select either class ID to filter or \"all\" classes", type=str)
    parser.add_argument("--img_w", help="Enter the width in pixel of video image frame", type=int)
    parser.add_argument("--img_h", help="Enter the height in pixel of video image frame", type=int)
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_args()
    input_dir_gt = args.input_dir_gt # file path to the directory that contains our ground truth 
    output_dir_gt = args.output_dir_gt  # file path to the directory that contains converted ground truth
    class_id_filter = args.class_id_filter
    img_w = args.img_w
    img_h = args.img_h
    output_path_gt = f"{output_dir_gt}/gt.txt" # file path to the single converted GT file

    if class_id_filter == "all":
        # ----------------------------------------------------------------
        # Generate GT file in MOT format for "all" classes
        # ----------------------------------------------------------------
        print("Converting GT file in MOT format for \"all\" classes ...")
        alltxt_gt = natural_sort(glob.glob(f"{input_dir_gt}/*.txt"))
        if os.path.exists(output_path_gt):
            os.remove(output_path_gt)
        classmap = dict()
        obj_count = 0
        with open(output_path_gt, 'a') as output_file:
            for txt in tqdm(alltxt_gt):
                frame = int(txt.split("_")[-1].split(".")[0]) + 1
                class_id, object_id, x, y, w, h = np.genfromtxt(txt, unpack=True)

                # Either numpy array or single value if txt contains only one row
                if isinstance(class_id, np.ndarray):
                    frame_id = np.repeat(frame, len(class_id))
                    conf_arr = np.repeat(1, len(class_id))  # for ground truth, confidence score is 1
                    pos_x_3d = np.repeat(-1, len(class_id)) # not 3d, so assign -1
                    pos_y_3d = np.repeat(-1, len(class_id)) # not 3d, so assign -1
                    pos_z_3d = np.repeat(-1, len(class_id)) # not 3d, so assign -1
                else:
                    frame_id = frame
                    conf_arr = 1 # for ground truth, confidence score is 1
                    pos_x_3d = -1 # not 3d, so assign -1
                    pos_y_3d = -1 # not 3d, so assign -1
                    pos_z_3d = -1 # not 3d, so assign -1

                # conversion of bbox parameters from relative coordinates to absolute coordinates
                x = normalize(x, 0, 1, 0, img_w)
                y = normalize(y, 0, 1, 0, img_h)
                w = normalize(w, 0, 1, 0, img_w)
                h = normalize(h, 0, 1, 0, img_h)

                # x1 y1 is top-left, x2 y2 is bottom-right
                x1 = x - w / 2
                y1 = y - h / 2
                # x2 = x + w / 2
                # y2 = y + h / 2 

                # object_id conversion for GT file
                # the following algorithm will map all the object_id indifferent to class_id
                data = np.array([frame_id, class_id, object_id, x1, y1, w, h, conf_arr, pos_x_3d, pos_y_3d, pos_z_3d]).T
                if data.ndim > 1:
                    # go through row by row
                    for i in range(len(data[:,1])):
                        # add new class id in classmap if it doesn't exist
                        if data[i,1] not in classmap:
                            classmap[data[i,1]] = dict()
                        old_obj_id = data[i,2]

                        # if old object id is in classmap[class_id] dictionary
                        # new object found!
                        if old_obj_id not in classmap[data[i,1]]:
                            obj_count += 1
                            new_obj_id = obj_count
                            data[i,2] = new_obj_id
                            classmap[data[i,1]][old_obj_id] = new_obj_id
                        # previously found object again
                        else:
                            new_obj_id = classmap[data[i,1]][old_obj_id]
                            data[i,2] = new_obj_id
                
                # In case of only 1 row in a txt file, i.e., 1d numpy array
                else:
                    if data[1] not in classmap:
                        classmap[data[1]] = dict()
                    old_obj_id = data[2]
                    if old_obj_id not in classmap[data[1]]:
                        obj_count += 1
                        new_obj_id = obj_count
                        data[2] = new_obj_id
                        classmap[data[1]][old_obj_id] = new_obj_id
                    else:
                        new_obj_id = classmap[data[1]][old_obj_id]
                        data[2] = new_obj_id

                frame_id, class_id, object_id, x1, y1, w, h, conf_arr, pos_x_3d, pos_y_3d, pos_z_3d = data.T

                # save (appending) into output_path_gt file
                np.savetxt(output_file, np.column_stack(\
                    (frame_id, object_id, x1, y1, w, h, conf_arr, pos_x_3d, pos_y_3d, pos_z_3d)\
                        ), delimiter=',', fmt="%d,%d,%s,%s,%s,%s,%d,%d,%d,%d")
                frame += 1

    else:
        # ----------------------------------------------------------------
        # Generate GT file in MOT format for the specific class_id
        # ----------------------------------------------------------------
        print(f"Converting GT file in MOT format for class_id {class_id_filter} ...")
        class_id_filter = int(class_id_filter) # we have to use integer to filter numpy 2d array
        alltxt_gt = natural_sort(glob.glob(f"{input_dir_gt}/*.txt"))
        if os.path.exists(output_path_gt):
            os.remove(output_path_gt)

        with open(output_path_gt, 'a') as output_file:
            for txt in tqdm(alltxt_gt):
                frame = int(txt.split("_")[-1].split(".")[0]) + 1
                class_id, object_id, x, y, w, h = np.genfromtxt(txt, unpack=True)

                # Either numpy array or single value if txt contains only one row
                if isinstance(class_id, np.ndarray):
                    frame_id = np.repeat(frame, len(class_id))
                    conf_arr = np.repeat(1, len(class_id))  # for ground truth, confidence score is 1
                    pos_x_3d = np.repeat(-1, len(class_id)) # not 3d, so assign -1
                    pos_y_3d = np.repeat(-1, len(class_id)) # not 3d, so assign -1
                    pos_z_3d = np.repeat(-1, len(class_id)) # not 3d, so assign -1
                else:
                    frame_id = frame
                    conf_arr = 1  # for ground truth, confidence score is 1
                    pos_x_3d = -1 # not 3d, so assign -1
                    pos_y_3d = -1 # not 3d, so assign -1
                    pos_z_3d = -1 # not 3d, so assign -1

                # conversion of bbox parameters from relative coordinates to absolute coordinates
                x = normalize(x, 0, 1, 0, img_w)
                y = normalize(y, 0, 1, 0, img_h)
                w = normalize(w, 0, 1, 0, img_w)
                h = normalize(h, 0, 1, 0, img_h)

                # x1 y1 is top-left, x2 y2 is bottom-right
                x1 = x - w / 2
                y1 = y - h / 2
                # x2 = x + w / 2
                # y2 = y + h / 2 

                # The following code will filter by class_id
                # pack data
                data = np.array([frame_id, class_id, object_id, x1, y1, w, h, conf_arr, pos_x_3d, pos_y_3d, pos_z_3d]).T
                
                # if data is 2D numpy array
                if data.ndim > 1:
                    data = data[data[:,1]==class_id_filter] # filtering by the class id
                    data[:, 2] += 1 # increment object id by 1 to start from 1 not 0
                
                # if data is 1D numpy array
                else:
                    if data[1] != class_id_filter:
                        continue
                    else:
                        data[2] += 1 # increment object id by 1 to start from 1 not 0
                frame_id, class_id, object_id, x1, y1, w, h, conf_arr, pos_x_3d, pos_y_3d, pos_z_3d = data.T

                # save (appending) into output_path_gt
                np.savetxt(output_file, np.column_stack(\
                    (frame_id, object_id, x1, y1, w, h, conf_arr, pos_x_3d, pos_y_3d, pos_z_3d)\
                        ), delimiter=',', fmt="%d,%d,%s,%s,%s,%s,%d,%d,%d,%d")