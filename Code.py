import cv2
import numpy as np
import math
from collections import deque
from abc import ABC, abstractmethod

#Abstract Object
class DrawObject(ABC):
    
    @abstractmethod
    def __init__(self,color,size):
        pass
    
    def getPoints(self):
        return self.points
    
    def getColor(self):
        return self.color
    
    def getSize(self):
        return self.size
    
    @abstractmethod
    def getTool(self):
        pass
    
    def setColor(self, col):
        self.color = col
        
    def setSize(self,siz):
        self.size = siz
    
    @abstractmethod
    def addPoint(self,pnt):
        pass
    
    @abstractmethod
    def draw(self,camera,canvas):
        pass


class DrawBrush(DrawObject):
    points = deque(maxlen=1024)
    
    def __init__(self, color, size):
        self.color = color
        self.size = size
        self.points = deque(maxlen = 512)
    
    def getTool(self):
        return 0
    
    def addPoint(self,pnt):
        self.points.appendleft(pnt)
    
    def draw(self, camera, canvas):
        for j in range(1,len(self.points)):
            if self.points[j-1] is not None and self.points[j] is not None:
                cv2.line(camera, self.points[j-1], self.points[j], self.color, self.size)
                cv2.line(canvas, self.points[j-1], self.points[j], self.color, self.size)

class DrawLine(DrawObject):
    points = deque(maxlen=3)
    
    def __init__(self, color, size):
        self.color = color
        self.size = size
        self.points = deque(maxlen = 3)
    
    def getTool(self):
        return 1
    
    def addPoint(self,pnt):
        if len(self.points) < 2:
            self.points.append(pnt)
        else:
            self.points[1] = pnt
            
    def draw(self, camera, canvas):
        if len(self.points) >= 2:
            cv2.line(camera, self.points[0], self.points[1], self.color, self.size)
            cv2.line(canvas, self.points[0], self.points[1], self.color, self.size)

class DrawRectangle(DrawObject):
    points = deque(maxlen=3)
    
    def __init__(self, color, size):
        self.color = color
        self.size = size
        self.points = deque(maxlen = 3)
    
    def getTool(self):
        return 2
    
    def addPoint(self,pnt):
        if len(self.points) < 2:
            self.points.append(pnt)
        else:
            self.points[1] = pnt
            
    def draw(self, camera, canvas):
        if len(self.points) >= 2:
            cv2.rectangle(camera, self.points[0], self.points[1], self.color, self.size)
            cv2.rectangle(canvas, self.points[0], self.points[1], self.color, self.size)
            
class DrawCircle(DrawObject):
    points = deque(maxlen=3)
    
    def __init__(self, color, size):
        self.color = color
        self.size = size
        self.points = deque(maxlen = 3)
    
    def getTool(self):
        return 3
    
    def addPoint(self,pnt):
        if len(self.points) < 2:
            self.points.append(pnt)
        else:
            self.points[1] = pnt
            
    def draw(self, camera, canvas):
        if len(self.points) >= 2:
            dist = int(math.dist(list(self.points[0]),list(self.points[1])))
            cv2.circle(camera, self.points[0], dist, self.color, self.size)
            cv2.circle(canvas, self.points[0], dist, self.color, self.size)
        
def setValues(x):
    a = 2
                        
currentTool = 0
customColor = (0,0,0)
paints = [DrawBrush((0,0,0),2)]
paintIndex = 0
undoDebounce = False            
            
kernel = np.ones((5, 5), np.uint8)

    

cv2.namedWindow("Color Detection")
cv2.createTrackbar("UpperHue", "Color Detection",
                   90, 180, setValues)
cv2.createTrackbar("UpperSat", "Color Detection",
                   255, 255, setValues)
cv2.createTrackbar("UpperVal", "Color Detection",
                   255, 255, setValues)
cv2.createTrackbar("LowerHue", "Color Detection",
                   60, 180, setValues)
cv2.createTrackbar("LowerSat", "Color Detection",
                   72, 255, setValues)
cv2.createTrackbar("LowerVal", "Color Detection",
                   49, 255, setValues)


# Create videocapture object
cap = cv2.VideoCapture(0)

size = cap.read()[1].shape

paint = np.zeros(size) + 255

cv2.createTrackbar("UpperRad", "Color Detection",
                   75, min([size[0],size[1]]), setValues)
cv2.createTrackbar("LowerRad", "Color Detection",
                   25, min([size[0],size[1]]), setValues)

toolList = "Tools: 0(Brush), 1(Line), 2(Rectangle), 3(Circle)\n"

cv2.namedWindow("Toolbox")
cv2.createTrackbar("Red", "Toolbox", 0, 255, setValues)
cv2.createTrackbar("Green", "Toolbox", 0, 255, setValues)
cv2.createTrackbar("Blue", "Toolbox", 0, 255, setValues)
cv2.createTrackbar("Size", "Toolbox", 1, 19, setValues)
cv2.createTrackbar(toolList, "Toolbox", 0, 3, setValues)

#cv2.resizeWindow("Color Detection",200,200)
#cv2.resizeWindow("Toolbox",200,200)

while True:
    customColor = (cv2.getTrackbarPos("Blue","Toolbox"),
                   cv2.getTrackbarPos("Green","Toolbox"),
                   cv2.getTrackbarPos("Red","Toolbox"))
    
    paintSize = cv2.getTrackbarPos("Size","Toolbox")+1
    currentTool = cv2.getTrackbarPos(toolList, "Toolbox")
    
    #Create new group if brush settings are different
    if(paints[paintIndex].getColor() != customColor):
        if len(paints[paintIndex].getPoints()) == 0:
            paints[paintIndex].setColor(customColor)
        else:
            if currentTool == 0:
                paints.append(DrawBrush(customColor,paintSize))
            elif currentTool == 1:
                paints.append(DrawLine(customColor,paintSize))
            elif currentTool == 2:
                paints.append(DrawRectangle(customColor,paintSize))
            elif currentTool == 3:
                paints.append(DrawCircle(customColor,paintSize))
            paintIndex += 1
    
    if(paints[paintIndex].getSize() != paintSize):
        if len(paints[paintIndex].getPoints()) == 0:
            paints[paintIndex].setSize(paintSize)
        else:
            if currentTool == 0:
                paints.append(DrawBrush(customColor,paintSize))
            elif currentTool == 1:
                paints.append(DrawLine(customColor,paintSize))
            elif currentTool == 2:
                paints.append(DrawRectangle(customColor,paintSize))
            elif currentTool == 3:
                paints.append(DrawCircle(customColor,paintSize))
            paintIndex += 1
    
    if(paints[paintIndex].getTool() != currentTool):
        if len(paints[paintIndex].getPoints()) == 0:
            if currentTool == 0:
                paints[paintIndex] = DrawBrush(customColor,paintSize)
            elif currentTool == 1:
                paints[paintIndex] = DrawLine(customColor,paintSize)
            elif currentTool == 2:
                paints[paintIndex] = DrawRectangle(customColor,paintSize)
            elif currentTool == 3:
                paints[paintIndex] = DrawCircle(customColor,paintSize)
        else:
            if currentTool == 0:
                paints.append(DrawBrush(customColor,paintSize))
            elif currentTool == 1:
                paints.append(DrawLine(customColor,paintSize))
            elif currentTool == 2:
                paints.append(DrawRectangle(customColor,paintSize))
            elif currentTool == 3:
                paints.append(DrawCircle(customColor,paintSize))
            paintIndex += 1
    
    #Key presses for clearing canvas and switching tools
    keypress = cv2.waitKey(1)
    
    if keypress & 0xFF == ord('c'):
        if currentTool == 0:
            paints = [DrawBrush(customColor,paintSize)]
        elif currentTool == 1:
            paints = [DrawLine(customColor,paintSize)]
        elif currentTool == 2:
            paints = [DrawRectangle(customColor,paintSize)]
        elif currentTool == 3:
            paints = [DrawCircle(customColor,paintSize)]
        paintIndex = 0
    #Undo
    elif keypress & 0xFF == ord('z'):
        if not undoDebounce:
            undoDebounce = True
            latestIndex = len(paints)-1
            if len(paints[latestIndex].getPoints()) > 0:
                if currentTool == 0:
                    paints[latestIndex] = DrawBrush(customColor,paintSize)
                elif currentTool == 1:
                    paints[latestIndex] = DrawLine(customColor,paintSize)
                elif currentTool == 2:
                    paints[latestIndex] = DrawRectangle(customColor,paintSize)
                elif currentTool == 3:
                    paints[latestIndex] = DrawCircle(customColor,paintSize)
            else:
                if len(paints) > 1:
                    paints.pop(len(paints)-2)
                    paintIndex -=1
                else:
                    if currentTool == 0:
                        paints = [DrawBrush(customColor,paintSize)]
                    elif currentTool == 1:
                        paints = [DrawLine(customColor,paintSize)]
                    elif currentTool == 2:
                        paints = [DrawRectangle(customColor,paintSize)]
                    elif currentTool == 3:
                        paints = [DrawCircle(customColor,paintSize)]
                    paintIndex = 0
    
    if keypress == -1:
        undoDebounce = False
        
    
    # Read each frame from webcam
    success, cam = cap.read()
    cam = cv2.flip(cam, 1)
    paint = np.zeros(size) + 255
    hsv = cv2.cvtColor(cam, cv2.COLOR_BGR2HSV)
    
    upHue = cv2.getTrackbarPos("UpperHue","Color Detection")
    upSat = cv2.getTrackbarPos("UpperSat","Color Detection")
    upVal = cv2.getTrackbarPos("UpperVal","Color Detection")
    lowHue = cv2.getTrackbarPos("LowerHue","Color Detection")
    lowSat = cv2.getTrackbarPos("LowerSat","Color Detection")
    lowVal = cv2.getTrackbarPos("LowerVal","Color Detection") 
    upperRad = cv2.getTrackbarPos("UpperRad", "Color Detection")
    lowerRad = cv2.getTrackbarPos("LowerRad", "Color Detection")
    
    upHSV = np.array([upHue,upSat,upVal])
    lowHSV = np.array([lowHue,lowSat,lowVal])
    
    mask = cv2.inRange(hsv, lowHSV, upHSV)
    mask = cv2.erode(mask, kernel, iterations = 1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations = 1)
    
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    center = None

    
    if(len(cnts) > 0):
        
        # Getting the center point
        cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
        
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        
        cv2.circle(cam, (int(x), int(y)), int(radius), (255, 255, 0) if (radius < upperRad and radius > lowerRad) else (0, 0, 255), 2)
    
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        # Incrementing points
        if(radius < upperRad and radius > lowerRad):
            paints[paintIndex].addPoint(center)
        elif len(paints[paintIndex].getPoints()) > 0:
            if currentTool == 0:
                paints.append(DrawBrush(customColor,paintSize))
            elif currentTool == 1:
                paints.append(DrawLine(customColor,paintSize))
            elif currentTool == 2:
                paints.append(DrawRectangle(customColor,paintSize))
            elif currentTool == 3:
                paints.append(DrawCircle(customColor,paintSize))
            paintIndex += 1
    elif len(paints[paintIndex].getPoints()) > 0:
        if currentTool == 0:
            paints.append(DrawBrush(customColor,paintSize))
        elif currentTool == 1:
            paints.append(DrawLine(customColor,paintSize))
        elif currentTool == 2:
            paints.append(DrawRectangle(customColor,paintSize))
        elif currentTool == 3:
            paints.append(DrawCircle(customColor,paintSize))
        paintIndex += 1
    
    # Drawing
    for i in paints:
        i.draw(cam,paint)
    
    cv2.imshow("Camera", cam)
    cv2.imshow("Mask", mask)
    cv2.imshow("Paint", paint)
    
    # Open the OpenCV window until 'q' is pressed
    if keypress & 0xFF == ord('q'):
        break
        
cap.release()


cv2.destroyAllWindows()