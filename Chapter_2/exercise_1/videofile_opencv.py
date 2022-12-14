import cv2
from base_camera import BaseCamera
import time

class Camera(BaseCamera):
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            ret, img = camera.read()
            time.sleep(0.02)
            if not ret:
                break
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # return img
            yield img
