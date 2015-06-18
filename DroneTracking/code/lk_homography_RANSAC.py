#!/usr/bin/env python

'''
Lucas-Kanade homography tracker
===============================

We used Lucas-Kanade sparse optical flow for tracking moving objects, uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames and finds homography between reference and current views, and use RANSAC for better fitting.
Also, we used convexHull, in order to identify an object with one flow but it yields less accurate results.

'''

import numpy as np
import cv2

def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)


lk_params = dict( winSize  = (19, 19),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 1000,
                       qualityLevel = 0.01,
                       minDistance = 5,
                       blockSize = 19 )

#find a good correspondence between consequtive points of interest 
#by backprojecting of the next frame points and choose the points which close enough
def checkedTrace(img0, img1, p0, back_threshold = 1.0):
    p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
    p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
    d = abs(p0-p0r).reshape(-1, 2).max(-1)
    status = d < back_threshold
    return p1, status
    
def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)


green = (0, 255, 0)
red = (0, 0, 255)


class App:
    def __init__(self, video_src):
        self.cam = cv2.VideoCapture(r'..\input\optical_flow_input.avi')
        self.p0 = None

    def run(self):
        
        fourcc = cv2.cv.CV_FOURCC(*'XVID')

        out = cv2.VideoWriter('homog.avi',fourcc, 20.0, (720,480))
        i=1
        while True:
            ret, frame = self.cam.read()
            #print frame.shape
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vis = frame.copy()
            vis_convex = vis.copy()
            if self.p0 is not None:
                p2, trace_status = checkedTrace(self.gray1, frame_gray, self.p1)
                
                
                self.p1 = p2[trace_status].copy()
                self.p0 = self.p0[trace_status].copy()
                
                self.gray1 = frame_gray
                
                               
                
                if len(self.p0) < 4:
                    self.p0 = None
                    continue
                

                
                p1c = []
                con_p1 = cv2.convexHull(self.p1, returnPoints=True)
                for con in con_p1:
                    cen, _ = cv2.minEnclosingCircle(con)
                    p1c.append(cen)
                
                
                p1c1 = []
                con_p1 = cv2.convexHull(np.int32(p1c), returnPoints=True)
                for con in con_p1:
                    cen, _ = cv2.minEnclosingCircle(con)
                    p1c1.append(cen)
                
                
                p0c = []
                con_p0 = cv2.convexHull(self.p0,returnPoints=True)                
                for con in con_p0:
                    cen, _ = cv2.minEnclosingCircle(con)
                    p0c.append(cen)
                 
                p0c0 = [] 
                con_p0 = cv2.convexHull(np.int32(p1c),returnPoints=True)                
                for con in con_p0:
                    cen, _ = cv2.minEnclosingCircle(con)
                    p0c0.append(cen)
                    
                #used homography and RANSAC for better fitting
                H, status = cv2.findHomography(self.p0, self.p1, cv2.RANSAC, 10.0)
                
                for (x0, y0), (x1, y1), good in zip(self.p0[:,0], self.p1[:,0], status[:,0]):
                    if good:
                        cv2.line(vis, (x0, y0), (x1, y1), (0, 128, 0))
                    cv2.circle(vis, (x1, y1), 2, (red, green)[good], -1)
                draw_str(vis, (20, 20), 'track count: %d' % len(self.p1))
                
                #used homography and RANSAC for better fitting
                H, status = cv2.findHomography(np.array(p0c0), np.array(p1c1), cv2.RANSAC, 10.0)
                
                for (x0, y0), (x1, y1), good in zip(np.int32(p0c0), np.int32(p1c1), status[:,0]):
                    if good:
                        cv2.line(vis_convex, (x0, y0), (x1, y1), (0, 128, 0))
                    cv2.circle(vis_convex, (x1, y1), 2, (red, green)[good], -1)
                draw_str(vis_convex, (20, 20), 'track count: %d' % len(np.int32(p1c1)))
                
            else:
                p = cv2.goodFeaturesToTrack(frame_gray, **feature_params)
                if p is not None:
                    for x, y in p[:,0]:
                        cv2.circle(vis, (x, y), 2, green, -1)
                    draw_str(vis, (20, 20), 'feature count: %d' % len(p))

            cv2.imshow('lk_homography', vis)
            cv2.imshow('lk_homography with convexhull', vis_convex)
            #cv2.imwrite('homog\\homog'+str(i)+'.jpg',vis)
            
            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break
            if i == 1:
                self.frame0 = frame.copy()
                self.p0 = cv2.goodFeaturesToTrack(frame_gray, **feature_params)

                if self.p0 is not None:
                    self.p1 = self.p0
                    self.gray0 = frame_gray
                    self.gray1 = frame_gray
                    
            i = i+1
         



def main():
    import sys
    try: video_src = sys.argv[1]
    except: video_src = 0

    App(video_src).run()
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
