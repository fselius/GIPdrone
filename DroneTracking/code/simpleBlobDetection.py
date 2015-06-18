# -*- coding: utf-8 -*-

'''
Simple Blob Detector

According to achieve a good tracking we tried the blob similarity creterions and try to adjust values for threshold.
At last, we choose to deffer foreground from background by color, 
we used frame subtraction and morphological operation, (eroion, dilation, opening and closing), 
to create white blobs for every moving object.


'''

from numpy import *
import numpy as np
import cv2


cap = cv2.VideoCapture(r'C:\Users\NoaMyara\Documents\drone_project\highway\input\in%06d.jpg')

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
fgbg = cv2.BackgroundSubtractorMOG2()
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter('blobDet3.avi',fourcc, 20.0, (320,240))
i=1
cpt = 0
while(1):
    
    ret, frame = cap.read()

    if frame==None:
        break
    
    #frame1 = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    vis = frame.copy()    
    
    fgmask = fgbg.apply(frame,None,0.03)
    
    kernelt = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
    kerneld = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(7,7))
    erosion = cv2.erode(fgmask,kerneld,iterations = 2)
    
    dil = cv2.dilate(erosion,kerneld,iterations = 3)
    opening = cv2.morphologyEx(dil, cv2.MORPH_OPEN, kernelt,iterations = 1)  
    erosion = cv2.erode(opening,kerneld,iterations = 1)
    dil = cv2.dilate(erosion,kerneld,iterations = 1) 
    

    
    closing = cv2.morphologyEx(dil, cv2.MORPH_CLOSE, kernel,iterations = 4)
    dilation = cv2.dilate(closing,kernel,iterations = 3)    
    closing2 = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernelt,iterations = 5)
    dilation2 = cv2.dilate(closing2,kernel,iterations = 5)

    regions = blobdet.detect(dilation2)
    
    if regions!=[]:
        drawing = np.zeros(frame.shape,np.uint8)
        edges = cv2.Canny(dilation,0,255,L2gradient=1)
        contours,hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            hull = cv2.convexHull(cnt)
            cv2.drawContours(drawing,[cnt],0,(255,255,255),10,2) # draw contours in green color
            cv2.drawContours(drawing,[hull],0,(0,0,255),2) # draw contours in red color
       
        cv2.drawKeypoints(vis,regions,vis, (0,255, 0),4)
        cv2.drawKeypoints(closing,regions,closing, (0,255, 0),4)
    cv2.imshow('frame', fgmask)
    cv2.imshow('erosion', erosion)
    cv2.imshow('dil', dil)
    cv2.imshow('opening', opening)
    #cv2.imshow('dilation', dilation)
    #cv2.imshow('closing', closing)
    #cv2.imshow('closing2', closing2)
    cv2.imshow('dilation2', dilation2)
    cv2.imshow('vis', vis)
    if i == 363:
        cv2.imwrite(r'out\image2%04i.jpg'%cpt,erosion)
        cv2.imwrite(r'out\image3%04i.jpg'%cpt,dilation2)

    cpt += 1
    fgmaskc = cv2.cvtColor(fgmask,cv2.COLOR_GRAY2BGR)
    erosionc = cv2.cvtColor(erosion,cv2.COLOR_GRAY2BGR)
    dilation2c = cv2.cvtColor(dilation2,cv2.COLOR_GRAY2BGR)
    

    allf = np.hstack((fgmaskc,erosionc,dilation2c,vis))
    #cv2.imshow('all',allf)
    #out.write(erosion)
    #out.write(dil)
    #out.write(dilation)
    #out.write(closing)
    #out.write(dilation2)
    #out.write(allf)
    cv2.imwrite('blob\\blob'+str(i)+'.jpg',allf)
    i = i+1
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()