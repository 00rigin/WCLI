
import logging as log

import cv2 as cv


class MulticamCapture:
    def __init__(self, sources):
        assert sources
        self.captures = []

        try:
            sources = [int(src) for src in sources]
            mode = 'cam'
        except ValueError:
            mode = 'video'

        if mode == 'cam':
            for id in sources:
                log.info('Connection  cam {}'.format(id))
                cap = cv.VideoCapture(id)
                # CPU 쓸때
                cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
                # MTRIAD 쓸때
                #cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
                #cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
                cap.set(cv.CAP_PROP_FPS, 30)
                cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))
                assert cap.isOpened()
                self.captures.append(cap)
        else:
            for video_path in sources:
                log.info('Opening file {}'.format(video_path))
                cap = cv.VideoCapture(video_path)
                assert cap.isOpened()
                self.captures.append(cap)

    def get_frames(self):
        frames = []
        for capture in self.captures:
            has_frame, frame = capture.read()
            if has_frame:
                frames.append(frame)

        return len(frames) == len(self.captures), frames

    def get_num_sources(self):
        return len(self.captures)
