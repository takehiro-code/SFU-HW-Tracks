# Metrics Evaluation

To compute the metrics for the object tracking performance from our dataset SFU-HW-Tracks-v1, we used the following source codes of tools to compute metrics:

- https://github.com/cheind/py-motmetrics [1]
- https://github.com/Cartucho/mAP [2]

py-motmetrics will compute various tracking metrics such as MOTA, MOTP, etc. We also included Cartucho/mAP to compute Mean Average Precision (mAP) which will assess detection accuracy. These are all in Python environment.

## Explanation
____

### Evaluating Object Tracking Metrics

1. Git clone cheind/py-motmetrics into your workspace or folder. Also, create the following folders from the command line:

`mkdir py-motmetrics/gt_dir`

`mkdir py-motmetrics/res_dir`

2. Convert the format of our ground truth files **[Class ID, Object ID, x, y, w, h]** to MOT challenge format **[Frame Index, Object ID, x1, y1, w, h, Confidence, 3D x, 3D y, 3D z]** since py-motmetrics accepts input in MOT format. 
Also, make sure your tracking results are in MOT challenge format as well. Note that py-motmetrics does not distinguish different class IDs, so you will be the one to determine whether to filter class ID during conversion.

Note: x, y refer to the center position of the bounding box. w, h are the dimensions of the bounding box. x1, y1 are the top-left corner of the bounding box. 3D x, 3D y, 3D z are the bounding box position in 3D, which are assigned as -1 since they are not applicable in our ground truth. They are all in relative coordinates.

3. Place the ground truth file in py-motmetrics/gt_dir/ and the tracking result in py-motmetrics/res_dir/. 

4. Run the following python script with inputs of ground truth in gt_dir/ and tracking results in res_dir/.

`python py-motmetrics/motmetrics/apps/eval_motchallenge.py py-motmetrics/gt_dir/ py-motmetrics/res_dir/
`

This will print the result in the console. You can modify eval_motchallenge.py to save the results in any other ways. 


### Evaluating mAP

1. Git clone Cartucho/mAP into your workspace or folder.

2. Convert our ground truth format **[Class ID, Object ID, x, y, ,w, h]** to PASCAL VOC format **[Class ID, x1, y1, x2, y2]**.
Make sure the detected result is in the form **[Class ID, Confidence, x1, y1, x2, y2]**.

Note: x2, y2 are the bottom-right corner of bounding box in a relative coordinate.

2. Place the ground truth files in input/ground-truth/ and input/detection-results/.

7. Run the following command to measure mAP.

`python mAP/main.py --no-animation --no-plot --quiet`

This will print the result in the console. You can modify <span>main.py</span> to save the result in any other ways.

## References
____
1. C. Heindl, “Cheind/py-motmetrics”, original-date: 2017-04-07T15:16:59Z, Mar. 24, 2021.
[Online]. Available: https : / / github . com / cheind / py - motmetrics (visited on
03/25/2021).
2. J. Cartucho, R. Ventura, and M. Veloso, “Robust object recognition through symbiotic deep
learning in mobile robots”, in 2018 IEEE/RSJ International Conference on Intelligent Robots
and Systems (IROS), ISSN: 2153-0866, Oct. 2018, pp. 2336–2341. doi: 10.1109/IROS.
2018.8594067.