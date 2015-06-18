#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================

Lucas-Kanade sparse optical flow demo. Uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.

Usage
-----
lk_track.py [<video_source>]


Keys
----
ESC - exit
'''

import numpy as np
import cv2



def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis


params = cv2.SimpleBlobDetector_Params()

params.filterByColor = 1
params.blobColor = 255

params.filterByArea = 0
params.minArea = 500
params.maxArea = 2000.

params.filterByCircularity = 0
params.minCircularity 
params.maxCircularity

params.filterByInertia = 0
params.minInertiaRatio = 0.60
params.maxInertiaRatio = 0.90
params.minDistBetweenBlobs = 0
#params.minThreshold = 140.
#params.maxThreshold = 255.
#params.thresholdStep = 10

blobdet = cv2.SimpleBlobDetector(params)

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.6,
                       minDistance = 30,
                       blockSize = 15)

class App:
    def __init__(self, video_src):
        self.track_len = 15
        self.detect_interval = 30
        self.tracks = []
        self.cam = cv2.VideoCapture(r'C:\Users\NoaMyara\Documents\drone_project\highway\input\in%06d.jpg')
        self.frame_idx = 0

    def run(self):
        fgbg = cv2.BackgroundSubtractorMOG()
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter('OptFlowDet.avi',fourcc, 20.0, (320,240))
        
        ret, prev = self.cam.read()
        prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, prev_gray, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        
        
        
        Z = flow.reshape((-1,2))
        
        # convert to np.float32
        Z = np.float32(Z)
        
        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 2
        ret,label,center=cv2.kmeans(Z,K,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
        
        # Now convert back into uint8, and make original image
        center = np.uint8(center)
        prev_res = center[label.flatten()]
        prev_res = prev_res[:,0]
        prev_res = prev_res.reshape((prev_gray.shape))
        #prev_res = prev_res[1][:][:]
        self.prev_gray = prev_res
        i=1
        #prev_res = prev_res.reshape((Z.shape))
        while True:
            ret, frame = self.cam.read()
            if frame==None:
                break
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(prev_gray, frame_gray, 0.5, 3, 15, 3, 5, 1.2, 0)
            #prevgray = frame_gray
            
            
            
            Z = flow.reshape((-1,2))
            
            # convert to np.float32
            Z = np.float32(Z)
            
            # define criteria, number of clusters(K) and apply kmeans()
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            K = 2
            ret,label,center=cv2.kmeans(Z,K,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
            
            # Now convert back into uint8, and make original image
            center = np.uint8(center)
            res = center[label.flatten()]
            
            res = res[:,0]      
            res = res.reshape((frame_gray.shape))
            new_res = res
            
            #frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vis = frame.copy()
            
            vis1 = frame.copy()
            
            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, res
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(res)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv2.circle(mask, (x, y), 5, 0, -1)
                p = cv2.goodFeaturesToTrack(res, mask = mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])
            
           
            #regions = blobdet.detect(new_res)
    
            #if regions!=[]:
            #   cv2.drawKeypoints(res,regions,vis1, (0,255, 0),4)

            #prev_res = res
            self.frame_idx += 1
            self.prev_gray = res
            prev_gray = frame_gray
            cv2.imshow('lk_track', vis)
            cv2.imshow('blob', vis1)
            cv2.imshow('flow', draw_flow(frame_gray, flow))
            cv2.imshow('res2', self.prev_gray)
            
            prevgray2c = cv2.cvtColor(self.prev_gray,cv2.COLOR_GRAY2BGR)
    

            allf = np.hstack((vis,prevgray2c))
            cv2.imshow('all',allf)
            cv2.imwrite('lk\\lk_track_kmeans'+str(i)+'.jpg',allf)
            i = i+1
            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break
         

def main():
    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    out = cv2.VideoWriter('lk_track_kmeans.avi',fourcc, 20.0, (320,240))
    import sys
    try: video_src = sys.argv[1]
    except: video_src = 0

    
    print __doc__
    App(video_src).run()
    out.release() 
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    
    main()
    

