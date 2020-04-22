# Multi Camera Multi Person Tracking

## How It Works

The demo expects the next models in the Intermediate Representation (IR) format:

   * Person detection model
   * Person re-identification model

If you want other model 

The demo workflow is the following:

1. The demo application reads tuples of frames from web cameras/videos one by one. For each frame in tuple it runs person detector
and then for each detected object it extracts embeddings using re-identification model.
2. All embeddings are passed to tracker which assigns an ID to each object.
3. The demo visualizes the resulting bounding boxes and unique object IDs assigned during tracking.

## Ready

### ready for NCS2

```bash
source setupvars.sh
cd install_dependencies
./install_NCS_udev_rules.sh
```

### Installation of dependencies

To install required dependencies run

```bash
pip3 install -r requirements.txt
```

## Running
### Command line arguments

1. connect NCS2
```
source setupvars.sh
```
2. choose at bellow
```
# videos
python3 multi_camera_multi_person_tracking.py \
    -i video4.mp4\
```
```
# webcam
python3 multi_camera_multi_person_tracking.py \
    -i 0 1\
```

### 피쳐값 위치
sct.py 에서 sct.get_tracks() 에서 튜플로 id, box location, feature 저장되있음 



## Demo Output

The demo displays bounding boxes of tracked objects and unique IDs of those objects.
To save output video with the result please use the option  `--output_video`, to change configuration parameters please open the `config.py` file and edit it.

Also demo can dump resulting tracks to a json file. To specify the file use the `--history_file` argument.

# WCLI
