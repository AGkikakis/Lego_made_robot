import numpy as np
# Enable the OpenCV 3 module. The module name is not changed to
# cv3 yet which could be quite confusing sometimes.
import cv2

class ColorIdentification:
    """
    Class contains method for identifing objects using color frequencies
    """

    def __init__(self):
        #######################################################################################################################
        ##                                          HSV ranges for different color                                         ####
        self.color_range = np.array([[np.array([100,190,120]), np.array([0,170,90]), np.array([20,150,90]),
                                      np.array([0,0,0]), np.array([0,0,210]), np.array([60,150,70]),
                                      np.array([10,150,90]),np.array([30,150,70])],
                                [np.array([110,255,200]), np.array([8,255,255]), np.array([25,255,255]),
                                np.array([255,255,50]), np.array([255,30,255]), np.array([75,255,255]),
                                np.array([12,255,255]), np.array([40,255,255])]])
        ## blue_lower   red_lower   yellow_lower   black_lower   white_lower   green_lower   orange_lower   light_green_lower ##
        ## blue_upper   red_upper   yellow_upper   black_upper   white_upper   green_upper   orange_upper   light_green_upper ##
        ########################################################################################################################
         #All objects' colorsself
        self.BLUE=0
        self.RED=1
        self.YELLOW=2
        self.BLACK=3
        self.WHITE=4
        self.GREEN=5
        self.ORANGE=6
        self.LIGHT_GREEN=7
        #self.objectsDetected
        #thres=+-20 if problem:
        self.threshold = 100
        # The spatial window radius
        self.xy_r = 20
        # The color window radius
        self.rgb_r = 30

    def identifyObject(self,img):
        """If an object is identified, module returns its color else returns None
        :param img:The image to scan for an object

        :return:None if nothing is found or the objects color(int)
        """
        #img=cv2.imread(img1)
        color=list()
        mask = list()
        #countour
        color_space = list()

        blur = cv2.blur(img, (6, 6))
        #identify white in rgb because it has highter accurancy!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        #meanshift_img = cv2.pyrMeanShiftFiltering(img, self.xy_r, self.rgb_r)
        hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        for i in range(0, 8):
            mask.append(cv2.inRange(hsv_img, self.color_range[0][i], self.color_range[1][i]))
            color_space.append(cv2.countNonZero(mask[i]))
            if color_space[i]-self.threshold > 0:
                if i<>4:
                    color.append(i)
                #print i
        if len(color)>1:
            for j in range(len(color)-1):
                print self.objectColor(color[j]),' | ',
            print self.objectColor(color[j+1])
        elif len(color)==1:print self.objectColor(color[0])
                # im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                #cv2.drawContours(img, contours, -1, (0,255,0), 3)
        #print '| '
        return color

    def objectColor(self,color):
        """Returns a string stating the color of the object detected"""
        switcher = {
        self.BLUE: "BLUE object Detected",
        self.RED: "RED object Detected",
        self.YELLOW: "YELLOW object Detected",
        self.BLACK:"BLACK object Detected",
        self.WHITE:"WHITE object Detected",
        self.GREEN: "GREEN object Detected",
        self.ORANGE:" ORANGE object Detected",
        self.LIGHT_GREEN:"LIGHT GREEN object Detected"
        }
        return switcher.get(color, None)

#    ##array with white
#    #######################################################################################################################
#        ##                                          HSV ranges for different color                                         ####
#        self.color_range = np.array([[np.array([100,190,120]), np.array([0,170,90]), np.array([20,150,90]),
#                                      np.array([0,0,0]), np.array([0,0,210]), np.array([60,150,70]),
#                                      np.array([10,150,90]),np.array([30,150,70])],
#                                [np.array([110,255,200]), np.array([8,255,255]), np.array([30,255,255]),
#                                np.array([255,255,50]), np.array([255,30,255]), np.array([75,255,255]),
#                                np.array([12,255,255]), np.array([40,255,255])]])
#        ## blue_lower   red_lower   yellow_lower   black_lower   white_lower   green_lower   orange_lower   light_green_lower ##
#        ## blue_upper   red_upper   yellow_upper   black_upper   white_upper   green_upper   orange_upper   light_green_upper ##
#        ########################################################################################################################