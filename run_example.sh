
## example shell script to measure tracking and detection performance ##

## Your ground truth path
gt_path='SFU-HW-Tracks-v1'

## example sequence for "person" class, class id 0
class_category='ClassC'
seq_name='PartyScene'
class_id="0"
img_w=832
img_h=480

# ---------------------------------------------------------------
# Set up
# ---------------------------------------------------------------

## git clone repositories if they don't exist
if [ ! -d py-motmetrics ]
then
    git clone https://github.com/cheind/py-motmetrics.git
fi

if [ ! -d mAP ]
then
    git clone https://github.com/Cartucho/mAP
fi

## unzip example detection and tracking results
if [ ! -d example ]
then
    unzip example.zip
fi

## set up directories in py-motmetrics
mkdir -p py-motmetrics/gt_dir
mkdir -p py-motmetrics/gt_dir/${class_category}_${seq_name}_${class_id}
mkdir -p py-motmetrics/gt_dir/${class_category}_${seq_name}_${class_id}/gt
mkdir -p py-motmetrics/res_dir

## for mAP, prepare COCO class id from 0 to 79
cp example/class_list.txt mAP/scripts/extra

# ---------------------------------------------------------------
# test MOT metrics
# ---------------------------------------------------------------

# Data format conversion of ground truth from modified YOLO to MOT
python yolo2mot.py\
    --input_dir_gt "${gt_path}/${class_category}/${seq_name}"\
    --output_dir_gt "py-motmetrics/gt_dir/${class_category}_${seq_name}_${class_id}/gt"\
    --class_id_filter ${class_id}\
    --img_w ${img_w}\
    --img_h ${img_h}

# prepare an example tracking result from example/ folder
cp example/tracking-results-example/ClassC_PartyScene_0.txt py-motmetrics/res_dir

# Evaluate tracking performance using cheind/py-motmetrics, inputting ground truth and result
python py-motmetrics/motmetrics/apps/eval_motchallenge.py py-motmetrics/gt_dir/ py-motmetrics/res_dir/

# ---------------------------------------------------------------
# test mAP
# ---------------------------------------------------------------

## Data format conversion of ground truth from modified YOLO to PASCAL VOC
rm mAP/input/ground-truth/*.txt
python yolo2voc.py\
    --input_dir_gt "${gt_path}/${class_category}/${seq_name}/"\
    --output_dir_gt "mAP/input/ground-truth"\
    --class_id_filter ${class_id}\
    --img_w ${img_w}\
    --img_h ${img_h}

# prepare an example detection result from example/ folder
rm mAP/input/detection-results/*.txt
cp example/detection-results-example/*.txt mAP/input/detection-results

# Evaluate mAP (in this case, IOU threshold of 0.5 set in mAP/main.py)
python mAP/main.py --no-animation --no-plot --quiet