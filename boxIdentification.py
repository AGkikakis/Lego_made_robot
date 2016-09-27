
import numpy as np
import cv2
import time


class BoxIdentification:


    def __init__(self,index):
        target=self.target(index)
        # Read the image of feature pattern
        print target
        self.template_matching = cv2.imread(target[0])
        #cv2.imshow('1',self.sign_img)
        #cv2.waitKey(0)
        # Filter the image in the same way as we did for the scene image and find the edges
        # sign_blur = cv2.GaussianBlur(sign_img, (11,11), 0)
        self.sign_blur = cv2.GaussianBlur(self.template_matching,(11,11), 0)
        self.sign_edges = cv2.Canny(self.sign_blur , 40, 150)
        #cv2.imshow('1',self.sign_edges)
        #cv2.waitKey(0)

        #########################################################
        #verification methods
        self.feature_matching = cv2.imread(target[1])
        # Detect the feature points in the object and the scene images
        # Create ORB feature detector object
        orb = cv2.ORB_create(nfeatures = 1000) # Set the maximum number of returned
                                               # feature points to 1000
        self.box_kp, self.box_des = orb.detectAndCompute(self.feature_matching, None)
        self.hasUsedVerificationAlg=False
        self.hasVerifiedTarget=False
        self.hasIdentfiedTarget=False
        self.boxLocation=None
        self.boxDistance=None
        self.showComments=False
        self.firstCheck=False
        self.ignoreTarget=False

    def identifyBox(self,image):

        start=time.time()
        self.scene_img=image
        #cv2.imshow('1',image)
        #cv2.waitKey(0)

        # Show the detected edges# Apply Gaussian blur to the image
        scene_blur = cv2.GaussianBlur(self.scene_img,  # input image
                                      (11,11),    # kernel size
                                      0)          # automatically calculate the standard
                                                  # deviation from the kernel size
        # Detect the edges
        scene_edges =cv2.Canny(scene_blur,20, 150)         # high threshold for the hysteresis procedure
        #scene_edges = cv2.Canny(cv2.cvtColor(scene_blur,cv2.CV_BGR2GRAY),20, 150)
        # Apply the distance transform to the image. The function returns the distance to the closest
        # zero valued pixel for each pixel.
        scene_dist = cv2.distanceTransform(~scene_edges,  # input image, edges are assumed to be black
                                           cv2.DIST_L2,   # use the L2 norm for pixel distance
                                           5)             # size of the distance transform mask

        # Normalise the distance to be in the range [0;1]. This step is not
        # strictly needed, however it provides image size invariance.
        cv2.normalize(scene_dist,      # input image
                      scene_dist,      # output image
                      0,               # min output value
                      1,               # max output value
                      cv2.NORM_MINMAX) # normalisation type

        # Show the normalised distance transform of the image
        #cv2.imshow('scene_dist', scene_dist)


        # Calculate the correlation coefficient between the distance transform
        # of the input image and the edges of the template image
        response = cv2.matchTemplate(scene_dist,             # input image
                                     np.float32(self.sign_edges), # template image
                                     cv2.TM_CCORR)           # calculate correlation coefficient

        # Technically, the calcualted response is not equal, but proportional to
        # the average edgel distance. Since we are interested in the location of
        # the global minimum we do not need to rescale the response.

        # Get the index of the minimum response. The argmin function transforms
        # the input array into 1D and then calculates the index of the minimum
        min_idx = np.argmin(response)
        # box_flag = 0 indicates no box found, box_flag = 1 indicates box found
        box_flag = 0

         # Get the 2D index from the 1D min_idx
        min_row, min_col = np.unravel_index(min_idx,        # input 1D index
                                            response.shape) # size of the 2D array

        # Get the top left corner of the detected object
        tl = (min_col, min_row)
        #
        # Get the the bottom right corner of the detected object
        br = (tl[0] + self.template_matching.shape[1],   # tl.x + template.width
                tl[1] + self.template_matching.shape[0])   # tl.y + template.height

        direction = (tl[0]+br[0])/2
        distance = (tl[1]+br[1])/2

        # threshold for the detect decision
        blue=self.blueDetector(self.scene_img)

        if distance>0 and distance<160:
               self.boxDistance='far'
        elif distance>160 and distance<320:
               self.boxDistance='not far'
        elif distance> 320 and distance<480:
               self.boxDistance='close'
        #If robot has detected an item
        if min_idx > 3000:
            if blue>0 and blue<5000:
                box_flag=1
                self.hasIdentfiedTarget=True
            elif blue>15000 and blue<25000:
                box_flag=1
                self.hasIdentfiedTarget=True
            else:box_flag=0
        else:box_flag=0

        if box_flag==0:
            print 'No Target'
            self.hasUsedVerificationAlg=False
            self.hasVerifiedTarget=False
            self.hasIdentfiedTarget=False
            self.ignoreTarget=False

        print 'Distance = ',self.boxDistance
        if self.boxDistance=='not far' or self.boxDistance=='close':
            if box_flag==1 and not self.hasUsedVerificationAlg:
                #print 'Identified object'
                if self.patternIdentification(image):
                    self.hasUsedVerificationAlg=True
                    self.hasVerifiedTarget=True
                    self.hasIdentfiedTarget=True
                else:
                    self.hasUsedVerificationAlg=True
                    self.hasVerifiedTarget=False
                    self.hasIdentfiedTarget=True
                    self.ignoreTarget=True

        #there is no blue lego inside the picture
        # if min_idx > 5000 and blue>0 and blue<2500:
        #     box_flag = 1
        # elif min_idx > 60000 and (blue>=2500 and blue<18000):
        #     if self.boxDistance=='close':
        #         box_flag = 0
        #     else:box_flag=1
        # else:
        #     box_flag = 0

        #print 'Direction = ', direction
        #print 'Distance = ',distance
        if box_flag == 1:
            if direction>0 and direction<213:
                self.boxLocation='left'
            elif direction>=213 and direction<427:
                self.boxLocation='middle'
            elif direction>=427 and direction<640:
                self.boxLocation='right'

        else:self.boxLocation=None

        #close =>brick=150 -50 ||
        #far => brick = 20-10
        #not far=>brick = 140-50 ||
        #print time.time()-start
        # print min_idx
        # print direction
        # print distance
        # Draw the rectangle of the detected image
        #self.blueDetector()
        if self.showComments:print  'Min Index = ',min_idx

        if box_flag==1 and self.hasVerifiedTarget:
            if self.showComments:print self.boxLocation
            if self.showComments:print self.boxDistance
            detected_img = cv2.rectangle(self.scene_img.copy(), tl, br, (0, 255, 0), 2)
        elif box_flag==1 and not self.hasVerifiedTarget:
            detected_img = cv2.rectangle(self.scene_img.copy(), tl, br, (0, 0, 255), 2)
        else:detected_img=self.scene_img

        return detected_img
        # Show the detected object
        #cv2.imshow('detected_img', detected_img)
        #cv2.waitKey(0)

    def blueDetector(self,image):
        hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        lower=np.array([105,150,50])
        upper= np.array([120,255,140])
        mask=cv2.inRange(hsv,lower,upper)
        bluespace=cv2.countNonZero(mask)
        if self.showComments:print 'Bluespace = ',bluespace
        return bluespace


    def patternIdentification(self,img):
        print 'Verifing Target...'
        start=time.time()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Run the Harris corner detector
        harris_response = cv2.cornerHarris(gray,   # Image to be procesed
                                            2,      # Size of the window (2x2)
                                            3,      # Size of the Sobel filter used to calculate
                                                    # the gradients. Can be 1, 3, 5 or 7.
                                            0.04)   # Value for the free prameter k
        # Calculate a threshold for the corner response
        thresh = 0.01 * harris_response.max()
        # Find all pixels which have harris detector response greater than the threshold
        corners = np.where(harris_response > thresh)

        # Create a copy of the scene image
        corners_image = img.copy()
        # Draw a circle centred at each detected corner
        for x, y in zip(corners[1], corners[0]):
             cv2.circle(corners_image,   # Image where to draw
                        (x, y),          # Centre of the circle
                        2,               # Radius of the circle
                        (0, 255, 0),     # Colour (B, G, R)
                        1)               # Line width
        # Show the image with corners

        # Create ORB feature detector object
        orb = cv2.ORB_create(nfeatures = 1000) # Set the maximum number of returned
                                                # feature points to 1000

        # Get the keypoints in the image and their descriptors.
        # The first argument is the image to be processed and
        # the second one is a mask specifying where to look for
        # keypoints. We have set it to `None` as it is optional.
        keypoints, descriptors = orb.detectAndCompute(img, None)

        # Visualise the keypoints
        kp_img = cv2.drawKeypoints(img,             # Processed image
                                    keypoints[:100],   # Draw only 100 of the detected keypoints
                                    None,              # Optional output image
                                    color=(0,255,255), # Colour which to draw the points with
                                    flags=4)           # Draw the orientation and the strength of the feature point



        # Create a brute force matcher object.
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, # Tells the matcher how to compare descriptors.
                                             # We have set it to use the hamming distance between
                                             # descriptors as ORB provides binary descriptors.
                           crossCheck=True)  # Enable cross check. This means that the matcher
                                             #  will return a matching pair [A, B] iff A is the
                                            # closest point to B and B is the closest to A.


        scene_kp, scene_des = orb.detectAndCompute(img, None)

        # Find the matching points using brute force
        matches = bf.match(scene_des, self.box_des)

        # Sort the matches in the order of the distance between the
        # matched descriptors. Shorter distance means better match.
        matches = sorted(matches, key = lambda m: m.distance)

        # Use only the best 1/10th of matchess
        matches = matches[:len(matches)/10]

        # Visualise the detected matching pairs
        match_vis = cv2.drawMatches(img,       # First processed image
                                    scene_kp,    # Keypoints in the first image
                                    self.feature_matching,         # Second processed image
                                    self.box_kp,      # Keypoints in the second image
                                    matches,     # Detected matches
                                    None)        # Optional output image
        # Create numpy arrays with the feature points in order to
        # estimate the homography between the two images.
        scene_pts = np.float32([scene_kp[m.queryIdx].pt for m in matches])
        box_pts = np.float32([self.box_kp[m.trainIdx].pt for m in matches])
        # Calculate the homography between the two images. The function works
        # by optimising the projection error between the two sets of points.
        H,mask = cv2.findHomography(box_pts,    # Source image
                                 scene_pts,  # Destination image
                                  cv2.RANSAC,) # Use RANSAC because it is very likely to have wrong matches
        #matchesMask = mask.tolist()
        #print matchesMask
        print 'Verification took ',time.time()-start, ' seconds'
        #print H
        #print matchesMask
        #print len(matchesMask)
        if float(cv2.countNonZero(np.asarray(mask)))/len(mask)<0.5:
            print 'Verification FAILED'
            return False
        else:
            print'Verification SUCCESSFULL'
            return  True
        #cv2.imshow('178',match_vis)
        #cv2.waitKey(0)
    def reset(self):
        self.hasUsedVerificationAlg=False
        self.hasIdentfiedTarget=False
        self.hasVerifiedTarget=False
        self.ignoreTarget=False
    def detectedBox(self):
        return self.hasIdentfiedTarget
    def identifiedTarget(self):
        return self.hasVerifiedTarget
    def whereIsBox(self):
        return self.boxLocation
    def howFarIsBox(self):
        return self.boxDistance
    def target(self,index):
        target={
            0:["supermario.png","supermario_full.png"],
            1:["futurama.png","futurama_full.png"],
            2:["zoidberg.png","zoidberg_full.png"],
            3:["wario.png","wario_full.png"]
        }
        return target.get(index,None)