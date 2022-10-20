import numpy as np
import cv2
import math

numPeople = 0
numPeopleIn = 0
numPeopleOut = 0

class Ringbuffer:
    def __init__(self, size):
        self.data = np.array([[0,0] for i in range(size)], dtype=np.uint16)
        self.size = size
        self.index = 0

    def put(self, value):
        #check for overflow
        if self.index == self.size:
            self.index = 0

        self.data[self.index] = np.array(value, dtype=np.uint16)
        self.index += 1
        return value

    def get(self):
        return self.data

class Person:
    class_counter= 0
    def __init__(self, direction, center_x, center_y, frame_num):

        Person.class_counter += 1
        self.id = str(Person.class_counter)
        self.direction = direction
        self.proximity_alert = False
        self.status = False

        self.center_x = center_x
        self.center_y = center_y
        self.centroids = Ringbuffer(12)
        self.last_updated_frame = frame_num

    def compare(self, new_center_x, new_center_y):
        return euclidean([self.center_x, self.center_y], [new_center_x, new_center_y])

    def update_data(self, new_center_x, new_center_y, frame_num):
        global numPeopleIn
        global numPeopleOut
        global led_manager

        self.center_x = new_center_x
        self.center_y = new_center_y
        self.centroids.put([new_center_x, new_center_y])

        y = []
        for c in self.centroids.get():
            if c[1] > 0:
                y.append(c[1])

        self.direction = self.center_y - sum(y)/len(y)

        if not self.status:

            if self.direction < -10 and self.center_y < 120:
                numPeopleIn += 1
                self.status = True

            elif self.direction > 10 and self.center_y > 120:
                numPeopleOut += 1
                self.status = True

        self.last_updated_frame = frame_num
        return {"id":self.id, "direction":self.direction, "proximityAlert":self.proximity_alert, "status":self.status}

class BoundBox:
    def __init__(self, x, y, w, h, c = None, classes = None):
        self.x     = x
        self.y     = y
        self.w     = w
        self.h     = h
        
        self.c     = c
        self.classes = classes

    def get_label(self):
        return np.argmax(self.classes)
    
    def get_score(self):
        return self.classes[self.get_label()]
    
    def iou(self, bound_box):
        b1 = self.as_centroid()
        b2 = bound_box.as_centroid()
        return centroid_box_iou(b1, b2)

    def as_centroid(self):
        return np.array([self.x, self.y, self.w, self.h])

def euclidean(a, b):
    s = 0
    for i in range(0, min(len(a), len(b))):
        s += (a[i] - b[i])**2
    return math.sqrt(s)

def centroid_box_iou(box1, box2):
    def _interval_overlap(interval_a, interval_b):
        x1, x2 = interval_a
        x3, x4 = interval_b
    
        if x3 < x1:
            if x4 < x1:
                return 0
            else:
                return min(x2,x4) - x1
        else:
            if x2 < x3:
                return 0
            else:
                return min(x2,x4) - x3
    
    _, _, w1, h1 = box1.reshape(-1,)
    _, _, w2, h2 = box2.reshape(-1,)
    x1_min, y1_min, x1_max, y1_max = to_minmax(box1.reshape(-1,4)).reshape(-1,)
    x2_min, y2_min, x2_max, y2_max = to_minmax(box2.reshape(-1,4)).reshape(-1,)
            
    intersect_w = _interval_overlap([x1_min, x1_max], [x2_min, x2_max])
    intersect_h = _interval_overlap([y1_min, y1_max], [y2_min, y2_max])
    intersect = intersect_w * intersect_h
    union = w1 * h1 + w2 * h2 - intersect
    
    return float(intersect) / union

def to_centroid(minmax_boxes):
    """
    minmax_boxes : (N, 4)
    """
    minmax_boxes = minmax_boxes.astype(np.float)
    centroid_boxes = np.zeros_like(minmax_boxes)
    
    x1 = minmax_boxes[:,0]
    y1 = minmax_boxes[:,1]
    x2 = minmax_boxes[:,2]
    y2 = minmax_boxes[:,3]
    
    centroid_boxes[:,0] = (x1 + x2) / 2
    centroid_boxes[:,1] = (y1 + y2) / 2
    centroid_boxes[:,2] = x2 - x1
    centroid_boxes[:,3] = y2 - y1
    return centroid_boxes

def to_minmax(centroid_boxes):
    centroid_boxes = centroid_boxes.astype(np.float)
    minmax_boxes = np.zeros_like(centroid_boxes)
    
    cx = centroid_boxes[:,0]
    cy = centroid_boxes[:,1]
    w = centroid_boxes[:,2]
    h = centroid_boxes[:,3]
    
    minmax_boxes[:,0] = cx - w/2
    minmax_boxes[:,1] = cy - h/2
    minmax_boxes[:,2] = cx + w/2
    minmax_boxes[:,3] = cy + h/2
    return minmax_boxes

def nms_boxes(boxes, n_classes, nms_threshold=0.3, obj_threshold=0.3):
    """
    # Args
        boxes : list of BoundBox
    
    # Returns
        boxes : list of BoundBox
            non maximum supressed BoundBox instances
    """
    # suppress non-maximal boxes
    for c in range(n_classes):
        sorted_indices = list(reversed(np.argsort([box.classes[c] for box in boxes])))

        for i in range(len(sorted_indices)):
            index_i = sorted_indices[i]
            
            if boxes[index_i].classes[c] == 0: 
                continue
            else:
                for j in range(i+1, len(sorted_indices)):
                    index_j = sorted_indices[j]

                    if boxes[index_i].iou(boxes[index_j]) >= nms_threshold:
                        boxes[index_j].classes[c] = 0
    # remove the boxes which are less likely than a obj_threshold
    boxes = [box for box in boxes if box.get_score() > obj_threshold]
    return boxes

def boxes_to_array(bound_boxes):
    """
    # Args
        boxes : list of BoundBox instances
    
    # Returns
        centroid_boxes : (N, 4)
        probs : (N, nb_classes)
    """
    centroid_boxes = []
    probs = []
    for box in bound_boxes:
        centroid_boxes.append([box.x, box.y, box.w, box.h])
        probs.append(box.classes)
    return np.array(centroid_boxes), np.array(probs)
