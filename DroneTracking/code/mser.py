#!/usr/bin/env python

'''
MSER - maximally stable region

According to achieve good tracking we tried many combination of mser parameters
and combination of color spaces, RGB, HSV. We found f = S/2 + v/2 worked quite well on our video.

Also, we smoothed the frame for getting smooth texture and use imresize for speed up the process. 

'''


import cv2


if __name__ == '__main__':

    cam = cv2.VideoCapture(r'..\input\yogaMat_MulHeight2_24.10.14.mp4')
    mser = cv2.MSER(1,0,94400,0.01,0.06,200,1.01,0.003,5)
    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    out = cv2.VideoWriter('MSER.avi',fourcc, 20.0, (320,240))
    #i=1
    while True:
        ret, img = cam.read()
        
        
        img = cv2.resize(img,(0,0), fx = 0.5, fy = 0.5)
           
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)        
        
        gray = s/2+v/2
        
        vis = img.copy()
        
        regions = mser.detect(gray, None)
        hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
        cv2.polylines(vis, hulls, 1, (0, 255, 0))
        
        #cv2.imwrite('mser\\mser'+str(i)+'.jpg',vis)
        #out.write(vis)
        cv2.imshow('img', vis)
        #i = i+1

        
        
        if 0xFF & cv2.waitKey(5) == 27:
            break
        
    out.release()
    cv2.destroyAllWindows()
