#!/usr/bin/env python

import numpy as np
import cv2

'''
we tried to use dense optical flow for detection of moving objects, 
it was accurate but slow, even when we reduced frame size and apply the algorithm every 50 frames only. 

'''



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

def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    hsv[...,2] = np.minimum(v*4, 255)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res

if __name__ == '__main__':
    import sys
    
    try: fn = cv2.VideoCapture(sys.argv[1])
    except: fn = 0

    cam = cv2.VideoCapture(r'..\input\optical_flow_input.avi')
    ret, prev = cam.read()
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    show_hsv = False
    show_glitch = False
    cur_glitch = prev.copy()
    i=0;
    while True:
        ret, img = cam.read()
        
        img = cv2.resize(img,(0,0), fx = 0.5, fy = 0.5)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if i%100 == 0:
            prevgray = gray
            i = i+1
            continue
        
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, 0.5, 3, 10, 3, 5, 1.2, 0)
        prevgray = gray
        
        i = i+1

        cv2.imshow('flow', draw_flow(gray, flow))
        
        cv2.imshow('flow HSV', draw_hsv(flow))
        

        ch = 0xFF & cv2.waitKey(5)
        if ch == 27:
            break
        

        
        
    cv2.destroyAllWindows()
 