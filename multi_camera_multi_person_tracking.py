
import argparse
import time
import queue
from threading import Thread
import json
import logging as log
import sys

import cv2 as cv

from utils.network_wrappers import Detector, VectorCNN
from mc_tracker.mct import MultiCameraTracker
from utils.misc import read_py_config
from utils.video import MulticamCapture
from utils.visualization import visualize_multicam_detections

from openvino.inference_engine import IECore # pylint: disable=import-error,E0611

log.basicConfig(stream=sys.stdout, level=log.DEBUG)


class FramesThreadBody:
    def __init__(self, capture, max_queue_length=2):
        self.process = True
        self.frames_queue = queue.Queue()
        self.capture = capture
        self.max_queue_length = max_queue_length

    def __call__(self):
        while self.process:
            if self.frames_queue.qsize() > self.max_queue_length:
                time.sleep(0.1)
            has_frames, frames = self.capture.get_frames()
            if not has_frames and self.frames_queue.empty():
                self.process = False
                break
            if has_frames:
                self.frames_queue.put(frames)


def run(params, capture, detector, reid): #params : args 임
    win_name = 'Multi camera tracking'
    config = {}

    if len(params.config):
        config = read_py_config(params.config)

    tracker = MultiCameraTracker(capture.get_num_sources(), reid, **config)

    thread_body = FramesThreadBody(capture, max_queue_length=len(capture.captures) * 2)
    frames_thread = Thread(target=thread_body)
    frames_thread.start()

    if len(params.output_video):
        video_output_size = (1920 // capture.get_num_sources(), 1080)
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        output_video = cv.VideoWriter(params.output_video,
                                      fourcc, 24.0,
                                      video_output_size)
    else:
        output_video = None

    while thread_body.process:
        start = time.time()
        try:
            frames = thread_body.frames_queue.get_nowait()
        except queue.Empty:
            frames = None

        if frames is None:
            continue

        all_detections = detector.get_detections(frames)
        #all_detections 좌표 성분 : ((left, right, top, bot), confidence) 값들의 리스트
        # 1번 영상의 디텍션 위치는 앞에 2번 영상의 디텍션 위치는 뒤에 표시됨
        # all_detextions : [[1번영상 사람들의 좌표, 컨디션], [2번 영상 사람들의 좌표, 컨디션]]
        all_masks = [[] for _ in range(len(all_detections))] # 디텍션 갯수만큼 비어있는 마스크 리스트 만듬
        for i, detections in enumerate(all_detections):
            all_detections[i] = [det[0] for det in detections]
            all_masks[i] = [det[2] for det in detections if len(det) == 3]

        """
        print("###################################")
        print("all_detections: ", all_detections)
        print("all_mask: ", all_masks)
        """

        tracker.process(frames, all_detections, all_masks)
        tracked_objects = tracker.get_tracked_objects()

        """print("###################################")"""
        #print(tracked_objects)
        
        ####################################################
        # ID 0 번만 찾게 만들기 (가상)
        """
        for i in range(len(tracked_objects)):
            _len = len(tracked_objects[i])
            for j in range(_len):
                print(i,j)
                #print((tracked_objects[i])[j])
                if ((tracked_objects[i])[j]).label is not "ID 0":
                    del (tracked_objects[i])[j]
                    _len = len(tracked_objects[i])
                    """
        #########################################################
    
        fps = round(1 / (time.time() - start), 1)
        vis = visualize_multicam_detections(frames, tracked_objects, fps)
        if not params.no_show:
            cv.imshow(win_name, vis)
            if cv.waitKey(1) == 27:
                break
        if output_video:
            output_video.write(cv.resize(vis, video_output_size))

    thread_body.process = False
    frames_thread.join()

    if len(params.history_file):
        history = tracker.get_all_tracks_history()
        with open(params.history_file, 'w') as outfile:
            json.dump(history, outfile)

def main():
    """Prepares data for the person recognition demo"""
    parser = argparse.ArgumentParser(description='Multi camera multi person \
                                                  tracking live demo script')
    parser.add_argument('-i', type=str, nargs='+', help='Input sources (indexes \
                        of cameras or paths to video files)', required=True)

    parser.add_argument('-m', '--m_detector', type=str, required=True,
                        help='Path to the person detection model')
    parser.add_argument('--t_detector', type=float, default=0.6,
                        help='Threshold for the person detection model')

    parser.add_argument('--m_reid', type=str, required=True,
                        help='Path to the person reidentification model')

    parser.add_argument('--output_video', type=str, default='', required=False)
    parser.add_argument('--config', type=str, default='', required=False)
    parser.add_argument('--history_file', type=str, default='', required=False)

    parser.add_argument('-d', '--device', type=str, default='CPU')
    parser.add_argument('-l', '--cpu_extension',
                        help='MKLDNN (CPU)-targeted custom layers.Absolute \
                              path to a shared library with the kernels impl.',
                             type=str, default=None)
    parser.add_argument("--no_show", help="Optional. Don't show output", action='store_true')

    args = parser.parse_args() 
    # 위에서 가져온 옵션에 대한 것들 args에 저장됨.
    # args.i 해서 옵션 i 에 저장된것 가져올 수 있음


    capture = MulticamCapture(args.i) # video.py 에 있는 클래스 변수에 포인터 지정함. capture 호출해서 그 안에 있는 함수 사용가능
    

    log.info("Creating Inference Engine")
    ie = IECore() #추론엔진 인터페이스 지정하기 (https://docs.openvinotoolkit.org/2019_R3/classie__api_1_1IECore.html)

    
    person_detector = Detector(ie, args.m_detector, args.t_detector,
                               args.device, args.cpu_extension,
                               capture.get_num_sources())
                               # capture.get_num_sources() : 영상의 갯수 
    if args.m_reid:
        person_recognizer = VectorCNN(ie, args.m_reid, args.device)
    else:
        person_recognizer = None
    run(args, capture, person_detector, person_recognizer)
    log.info('Demo finished successfully')


if __name__ == '__main__':
    main()
