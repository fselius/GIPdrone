import cv2
import numpy as np
import math
import glob
import sys

def imshow(img):
    cv2.imshow('f',img)
    cv2.waitKey(0)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()


def colorToBW(imgpath, blur = 0, thresh = "max"):
    img = cv2.imread(imgpath, cv2.CV_LOAD_IMAGE_COLOR)
    img = cv2.medianBlur(img, blur)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype('float32')
    h = hsv[:,:,0]
    v = hsv[:,:,2]
    mser_channel = ((h+v)/2.0)
    preK = mser_channel.reshape(-1)
    K = 3
    Kcriteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(preK, K, Kcriteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    center = np.uint8(center)
    res = center[label.flatten()].astype('uint8')
    res2 = res.reshape((mser_channel.shape))
    if thresh == "max":
        bw = cv2.threshold(res2, res2.max()-1,255, cv2.THRESH_BINARY)[1]
    else:
        bw = cv2.threshold(res2, res2.min()+1,255, cv2.THRESH_BINARY)[1]
    #imshow(bw)
    
    return (bw, img) 

def guessShape(imgname, blur = 0, thresh = "max", polyPerc = 0.03):
    #img, origImg = colorToBW(imgname, blur)
    img = cv2.imread(imgname, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    out = img.copy()
    ret, img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    
    # Gets a binary image and finds the contours
    cont = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
    areaMin = 200 # minimum area for contour
    output = None
    
    out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
    #lineColor = (0,255,0)
    lineThick = 2
    
    areas = map(lambda x: cv2.contourArea(x), cont)
    maxIndex = areas.index(max(areas))
    
    res = cv2.approxPolyDP(cont[maxIndex], polyPerc*cv2.arcLength(cont[maxIndex], True), True)
    if cv2.contourArea(res) > areaMin:
        lineDots = [(i[0][0],i[0][1]) for i in res]
        lineDots.append((res[0][0][0],res[0][0][1]))
        lineDots.append((res[1][0][0],res[1][0][1]))
        
        filterShape(lineDots)
        
        angs = np.zeros(len(lineDots)-2)
        linesLen = np.zeros(len(lineDots)-2)
        
        
        for x in range(0,len(lineDots)-2):
            cv2.line(out, lineDots[x], lineDots[x+1], colorize(x), lineThick)
            angs[x] = math.degrees(angleBetweenLines(line1 = (lineDots[x], lineDots[x+1]), line2 = (lineDots[x+1], lineDots[x+2])))
            linesLen[x] = lineLen((lineDots[x], lineDots[x+1]))
        
        
        linesLen = linesLen / linesLen.sum()
        #=======================================================================
        # 
        # if linesLen.min()/linesLen.max() < 0.3:
        #     output, ignore_ = guessShape(imgname, polyPerc = 0.05)
        #     return output, ignore_
        # 
        #=======================================================================
        printStats(angs, "Angles")
        printStats(linesLen, "Lines")
        
        if len(angs) == 3: output = "Triangle"
        
        if angs.sum() > 400.0:
            if len(angs) < 8 and polyPerc == 0.025:
                output, out = guessShape(imgname, polyPerc = 0.05)
                return output, out
            if len(angs) < 10:
                return "Arrow", out
            if len(angs) == 10 or len(angs) == 11:
                return "Star", out
            if len(angs) > 11:
                if angs.std() > 20:
                    return "David_star", out
                else:
                    return "Cross", out
        
        # 4 vertices
        if len(angs) == 4:
            if angs.std() > 30 and np.delete(angs,angs.argmin()).std() < 7.5:
                output = "Triangle"
            
            elif angs.std() < 7.5: # angles STD is less than 7.5 degrees
                if (linesLen/linesLen.max()).std() > 0.05: # if lines length STD is less than 5% -> rectangle, else -> square
                    output = "Rectangle"
                else:
                    output = "Square"
            else:
                if (linesLen/linesLen.max()).std() > 0.10: # if lines length STD is less than 10% -> Rhombus('meoyan'), else -> Trapezoid 
                    output = "Trapezoid"
                else:
                    output = "Rhombus"
        
        
        if angs.min() < 20 and len(angs) > 5:
            tmp = np.delete(angs, angs.argmin())
            
        if len(angs) == 5:
            if linesLen.std() > 0.05 and polyPerc == 0.03:
                output, ignore_ = guessShape(imgname, polyPerc = 0.025)
            else:
                output = "Pentagon"
        
        if len(angs) > 5:
            if angs.std() < 10:
                output = 'Circle'
            #elif angs.std() < 10:
            #    output, ignore_ = guessShape(imgname, polyPerc = 0.025)
            else:
                tmp = angs.copy()
                tmp = np.delete(tmp,tmp.argmax())
                tmp = np.delete(tmp,tmp.argmax())
                if tmp.std() < 10:
                    output = "Half_circle"
                
                elif abs(tmp.max()-90.0) < 7.5:
                    output = "Quarter_circle"
                
                elif abs(np.sort(angs)[-3:].mean() - 90) < 7.5:
                    output = "Quarter_circle"
                    
                printStats(tmp, "Temp angles")
        
        #print output,imgname
        #imshow(out)
    if output == None and polyPerc == 0.03:
        output, out = guessShape(imgname, polyPerc = 0.05)
    return output, out

def lineLen(line):
    vec = lineToVector(line[0],line[1])
    return math.sqrt(vec[0]**2 + vec[1]**2)

def angleBetweenLines(line1, line2):
    vec1 = lineToVector(line1[0],line1[1])
    vec2 = lineToVector(line2[0],line2[1])
    return angle(vec1, vec2)

def lineToVector(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return (x2-x1,y2-y1)

def angle(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    inner_product = x1*x2 + y1*y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    return math.acos(inner_product/(len1*len2))


# [(79, 19), (22, 26), (24, 87), (81, 77), (79, 19), (22, 26)]
def filterShape(vertice):
    angs = np.zeros(len(vertice)-2)
    linesLen = np.zeros(len(vertice)-2)
        
        
    for x in range(0,len(vertice)-2):
        angs[x] = math.degrees(angleBetweenLines(line1 = (vertice[x], vertice[x+1]), line2 = (vertice[x+1], vertice[x+2])))
        linesLen[x] = lineLen((vertice[x], vertice[x+1]))
    
    for x in range(0, len(angs)):
        if angs[x] < 20:
            #print angs[x],x
            pass
    
def printStats(arr,title):
    return 0
    print "### {} ###".format(title)
    print "Sum:\t\t","%.2f" % arr.sum()
    print "Mean:\t\t","%.2f" % arr.mean()
    print "STD:\t\t","%.2f" % arr.std()
    print "Values:"
    for i in range(0, len(arr), 3):
        print "\t\t".join(["%.2f" % x for x in arr[i:i+3]])
    print "\n"

def colorize(x):
    # Only first is white, second green
    if x == 0: return (255,0,255)
    s = x % 5
    if s == 0: return (255,0,0)
    if s == 1: return (0,255,0)
    if s == 2: return (255,255,0)
    if s == 3: return (0,0,255)
    if s == 4: return (0,255,255)

if __name__ == '__main__':
    try:
        pic = sys.argv[1]
        result,out  = guessShape(pic, blur = 0)
        print result
    except:
        print None