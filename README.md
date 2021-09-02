# Metrics Evaluation

To compute the metrics for the object tracking performance from our dataset SFU-HW-Tracks-v1, we used the following source codes of tools to compute metrics:

- https://github.com/cheind/py-motmetrics [[1]](#References)
- https://github.com/Cartucho/mAP [[2]](#References)

py-motmetrics will compute various tracking metrics such as MOTA, MOTP, etc. We also included Cartucho/mAP to compute Mean Average Precision (mAP) which will assess detection accuracy. These are all in Python3 environment.

## Explanation

We prepared `run_example.sh` to run the test measurement of various tracking metrics and detection performance mAP with the example results prepared in the `example` folder. You can unzip the example folder. You can also modify the shell script to your own needs. The description is as following.

### Evaluating Object Tracking Metrics

1. Git clone cheind/py-motmetrics into your workspace or folder. Also, set up the following directories from the command line:

`mkdir py-motmetrics/gt_dir`

`mkdir py-motmetrics/gt_dir/FOLDER_NAME/`

`mkdir py-motmetrics/gt_dir/FOLDER_NAME/gt`

`mkdir py-motmetrics/res_dir`

FOLDER_NAME is the same name as the file name of the tracking result `FILE_NAME.txt`, where you will place it as `py-motmetrics/res_dir/FILE_NAME.txt`

2. Convert the format of our ground truth files **[Class ID, Object ID, x, y, w, h]** (which is a modified version of YOLO output format, adding object_id in the second column) to MOT challenge format **[Frame Index, Object ID, x1, y1, w, h, Confidence, 3D x, 3D y, 3D z]** since py-motmetrics accepts input in MOT format. 
Also, make sure your tracking results are in MOT challenge format as well. 

Note: x, y refer to the center position of the bounding box. w, h are the dimensions of the bounding box. x1, y1 are the top-left corner of the bounding box. 3D x, 3D y, 3D z are the bounding box position in 3D, which are assigned -1 since they are not applicable in our ground truth. They are all in relative coordinates.

The script `yolo2mot.py` will do the conversion. The following arguments will be necessary to run the conversion:

- input_dir_gt: Directory path to the ground truth of the sequence.
- output_dir_gt: Directory path to the converted ground truth of the sequence, i.e., `py-motmetrics/gt_dir/FOLDER_NAME/gt`. Single ground truth file will be saved in `py-motmetrics/gt_dir/FOLDER_NAME/gt/gt.txt`. 
- class_id: Either "all" or the specific class id from 0 to 79 for COCO object classes.
- img_w: Video frame width that is used for conversion from relative coordinates to absolute coordinates.
- img_h: Video frame height that is used for conversion from relative coordinates to absolute coordinates.

Note that py-motmetrics does not distinguish different class IDs, so you will be the one to determine whether to select the specific class ID during conversion. If you don't want to select, pass "all" argument. We defined "all" as all the classes that exist in the ground truth.

3. Place the tracking result in `py-motmetrics/res_dir/`.

4. Run the following python script with inputs of ground truth in `gt_dir` and tracking results in `res_dir`.

`python py-motmetrics/motmetrics/apps/eval_motchallenge.py py-motmetrics/gt_dir/ py-motmetrics/res_dir/`

This will print the result in the console. You can modify `eval_motchallenge.py` to save the results in any other ways. 


### Evaluating mAP

1. Git clone Cartucho/mAP into your workspace or folder. Also, update `mAP/scripts/extra/class_list.txt` from our example folder to allow measuring mAP on COCO object classes.

2. Convert our ground truth format **[Class ID, Object ID, x, y, ,w, h]** to PASCAL VOC format **[Class ID, x1, y1, x2, y2]**.
Make sure the detected result is in the form **[Class ID, Confidence, x1, y1, x2, y2]**.

Note: x2, y2 are the bottom-right corner of bounding box in a relative coordinate.

The script `yolo2voc.py` will do the conversion. The following arguments will be necessary to run the script.

- input_dir_gt: Directory path to the ground truth of the sequence.
- output_dir_gt: Directory path to the converted ground truth of the sequence, i.e., `mAP/input/ground-truth`.
- class_id: Either "all" or the specific class id from 0 to 79 for COCO object classes.
- img_w: Video frame width that is used for conversion from relative coordinates to absolute coordinates.
- img_h: Video frame height that is used for conversion from relative coordinates to absolute coordinates.

2. Place the detection result in `mAP/input/detection-results/`.

7. Run the following command to measure mAP.

`python mAP/main.py --no-animation --no-plot --quiet`

The current `main.py` script measures mAP at IOU threshold of 0.5. Also, this script will print the result in the console. You can modify it to save the result in any other ways.

<a name="References"></a>
## References

1. C. Heindl, “Cheind/py-motmetrics”, original-date: 2017-04-07T15:16:59Z, Mar. 24, 2021.
[Online]. Available: https : / / github . com / cheind / py - motmetrics (visited on
03/25/2021).
2. J. Cartucho, R. Ventura, and M. Veloso, “Robust object recognition through symbiotic deep
learning in mobile robots”, in 2018 IEEE/RSJ International Conference on Intelligent Robots
and Systems (IROS), ISSN: 2153-0866, Oct. 2018, pp. 2336–2341. doi: 10.1109/IROS.
2018.8594067.