import io
import re
import time
import argparse
import cv2
import numpy as np
from utils import Person, nms_boxes, boxes_to_array, BoundBox, to_minmax

from tflite_runtime.interpreter import Interpreter
from flask import Flask, render_template, request, Response

app = Flask(__name__, static_url_path = '')

class Detector(object):

    def __init__(self, label_file, model_file, threshold):
        self._threshold = float(threshold)
        self.labels = self.load_labels(label_file)
        self.interpreter = Interpreter(model_file, num_threads=6)
        self.interpreter.allocate_tensors()
        _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']
        self.tensor_index = self.interpreter.get_input_details()[0]['index']

        self.people_list = []
        self.data = []
        self.frame_num = 0

    def load_labels(self, path):
        with open(path, 'r') as f:
            return {i: line.strip() for i, line in enumerate(f.read().replace('"','').split(','))}

    def preprocess(self, img):
        img = cv2.resize(img, (self.input_width, self.input_height))
        img = img.astype(np.float32)
        img = img / 255.
        img = img - 0.5
        img = img * 2.
        img = img[:, :, ::-1]
        img = np.expand_dims(img, 0)
        return img

    def get_output_tensor(self, index):
      """Returns the output tensor at the given index."""
      output_details = self.interpreter.get_output_details()[index]
      tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))
      return tensor

    def detect_objects(self, image):
      """Returns a list of detection results, each a dictionary of object info."""
      img = self.preprocess(image)
      self.interpreter.set_tensor(self.tensor_index, img)
      self.interpreter.invoke()
      # Get all output details
      boxes = self.get_output_tensor(0)
      return boxes

    def draw_overlay(self, image, boxes):

        num = 0
        people_data = {}

        for box in boxes:

            x1, y1, x2, y2 = box
            match = False

            center_x = (x1 + x2)//2
            center_y = (y1 + y2)//2

            print(center_x, center_y)

            for person in self.people_list:
                dist = person.compare(center_x, center_y)
                if dist < 70:
                    match = True
                    people_data[num] = person.update_data(center_x, center_y, self.frame_num)
                    break

            if not match:
                new_person = Person(direction=0, center_x=center_x, center_y=center_y, frame_num = self.frame_num)
                self.people_list.append(new_person)
                people_data[num] = new_person.update_data(center_x, center_y, self.frame_num)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0,255,0), 3)
            cv2.circle(image, (center_x, center_y), 2, (0,255,0), 3)

            cv2.putText(image, 
                        '{}'.format(people_data[num]["id"]), 
                        (x1, y1 - 13), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.0025 * image.shape[0], 
                        (0,255,0), 2)

            num += 1

        for person in self.people_list:
            if self.frame_num - person.last_updated_frame  > 10:
                self.people_list.remove(person)

        cv2.line(image, (0, self.output_height//2), (self.output_width, self.output_height//2), color = (0, 0, 255), thickness = 4) 

        return image

    def detect(self, original_image):

        self.output_height, self.output_width = original_image.shape[0:2]
        start_time = time.time()
        results = self.detect_objects(original_image)
        elapsed_ms = (time.time() - start_time) * 1000
        fps  = 1 / elapsed_ms*1000
        print("Estimated frames per second : {0:.2f} Inference time: {1:.2f}".format(fps, elapsed_ms))

        def _to_original_scale(boxes):
            if len(boxes) > 0:
                minmax_boxes = to_minmax(boxes)
                minmax_boxes[:,0] *= self.output_width
                minmax_boxes[:,2] *= self.output_width
                minmax_boxes[:,1] *= self.output_height
                minmax_boxes[:,3] *= self.output_height
                return minmax_boxes.astype(np.int)
            return []

        boxes, probs = self.run(results)
        boxes = _to_original_scale(boxes)

        print(boxes)
        overlay_image = self.draw_overlay(original_image, boxes)
        self.frame_num += 1

        return cv2.imencode('.jpg', overlay_image)[1].tobytes()

    def run(self, netout):
        anchors = [0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828]
        nms_threshold=0.2
        """Convert Yolo network output to bounding box
        
        # Args
            netout : 4d-array, shape of (grid_h, grid_w, num of boxes per grid, 5 + n_classes)
                YOLO neural network output array
        
        # Returns
            boxes : array, shape of (N, 4)
                coordinate scale is normalized [0, 1]
            probs : array, shape of (N, nb_classes)
        """
        grid_h, grid_w, nb_box = netout.shape[:3]
        boxes = []
        
        # decode the output by the network
        netout[..., 4]  = _sigmoid(netout[..., 4])
        netout[..., 5:] = netout[..., 4][..., np.newaxis] * _softmax(netout[..., 5:])
        netout[..., 5:] *= netout[..., 5:] > self._threshold
        
        for row in range(grid_h):
            for col in range(grid_w):
                for b in range(nb_box):
                    # from 4th element onwards are confidence and class classes
                    classes = netout[row,col,b,5:]
                    
                    if np.sum(classes) > 0:
                        # first 4 elements are x, y, w, and h
                        x, y, w, h = netout[row,col,b,:4]

                        x = (col + _sigmoid(x)) / grid_w # center position, unit: image width
                        y = (row + _sigmoid(y)) / grid_h # center position, unit: image height
                        w = anchors[2 * b + 0] * np.exp(w) / grid_w # unit: image width
                        h = anchors[2 * b + 1] * np.exp(h) / grid_h # unit: image height
                        confidence = netout[row,col,b,4]
                        box = BoundBox(x, y, w, h, confidence, classes)
                        boxes.append(box)
        
        boxes = nms_boxes(boxes, len(classes), nms_threshold, self._threshold)
        boxes, probs = boxes_to_array(boxes)
        return boxes, probs

def _sigmoid(x):
    return 1. / (1. + np.exp(-x))

def _softmax(x, axis=-1, t=-100.):
    x = x - np.max(x)
    if np.min(x) < t:
        x = x/np.min(x)*t
    e_x = np.exp(x)
    return e_x / e_x.sum(axis, keepdims=True)

@app.route ("/")
def index():
   return render_template('index.html', name = None)

def gen(camera):
    while True:
        frame = camera.get_frame()
        image = detector.detect(frame)
        yield (b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--model', help='File path of .tflite file.', required=True)
parser.add_argument('--labels', help='File path of labels file.', required=True)
parser.add_argument('--threshold', help='Confidence threshold.', default=0.3)
parser.add_argument('--source', help='picamera or cv', default='cv')
parser.add_argument('--file', help='path to file', default=None)
args = parser.parse_args()

if args.source == "cv":
    from camera_opencv import Camera
    source = 0
elif args.source == "picamera":
    from camera_pi import Camera
    source = 0
elif args.source == "file":
    from videofile_opencv import Camera
    source = args.file

Camera.set_video_source(source)

detector = Detector(args.labels, args.model, args.threshold)

if __name__ == "__main__" :
   app.run (host = '0.0.0.0', port = 5000, debug = True)
    
