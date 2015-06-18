#!/usr/bin/env python

'''
We used dense optical flow in order to find missing objects
'''

import numpy as np
import cv2



if __name__ == '__main__':

    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], '', ['feature='])
    opts = dict(opts)
    feature_name = opts.get('--feature', 'sift')


    img22 = cv2.imread(r'..\input\in000573.jpg')
    img11 = cv2.imread(r'..\input\in000608.jpg')
    
    img1= cv2.cvtColor(img11,cv2.COLOR_BGR2GRAY)
    img2= cv2.cvtColor(img22,cv2.COLOR_BGR2GRAY)
    

    detector, matcher = init_feature(feature_name)
    if detector != None:
        print 'using', feature_name
    else:
        print 'unknown feature:', feature_name
        sys.exit(1)
        
    hsv = np.zeros_like(img11)
    hsv[...,1] = 255
    
     
    flow = cv2.calcOpticalFlowFarneback(img1,img2,0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    cv2.imshow('frame1',img11)
    cv2.imshow('frame2',img22)
    
    cv2.imshow('dense optical flow',rgb)

    
    cv2.waitKey()
    cv2.destroyAllWindows()
