import time
import collections
import numpy
import position

### Ctl+p brings parameters while using a module etc control(a,b)###

class Toddler:
    # Initialiser
    def __init__(self,IO):
        # Print a message
        #Robot tends to go to the right direction if True
        self.rightBias=True
        self.comments=True
        print('Toddler Initialized')
        # Store the instance of IO for later
        self.IO=IO

        self.waitForVision=True
        self._pos=position.Position(self.IO,roomtoreach='B')
        self._irThreshold=480
        #Terminator rotates 360 when the mission starts
        self.justStared=True
        self.digitalInputs=self.IO.getSensors()
        self.analogInputs=self.IO.getInputs()
        self.spins=0
        #Terminators Basic Functions
        self._goal=0.1
        self.speed=0.1
        self.distanceToRotate90=0.155
        #List to prevent robot from getting stack
        self.l = collections.deque(maxlen=35)
        self.waitForVision=True
        #False when the robot starts, becomes true when robot identifies its position for the first time
        self.localized=False
        #Variables for pointing in which side of the robot the wall is
        self.hasWallonRight=False
        self.wallThreshold=150
        self.hasWallonLeft=False
        #Variable to denote if the robot found an edge and need to turn
        self.edge=False
        #Variable that denotes we changed room
        self.currentRoom=None

    def Control(self, OK):
        #print('Enter Control')
        # #Get Hall value to start measuring distance
        ########################TEST SENSORS################
        #self.rotate(180,False)
        #time.sleep(10)
#         while OK:
#             self.testSensors()
#             time.sleep(0.05)
        #######################################################
        ##################MAIN LOOP###########################
         if self.waitForVision:
             return True

         self.identifyRoom()
         self.setOrientation()

         while OK and (not self._pos.isMissionEnded())and not self.waitForVision:
              if self.currentRoom!=None and not self.localized:
                  self.setOrientation()
                  self.localized=True
              #if self._pos.isSartingPoint():
              if(not self.collision()):
                   #self._pos.isStartingPoint()
                   ##print'not collision'
                self.goStraight()
                   #self.coverDistance(0.05)
              #else:print ' collision'

              time.sleep(0.05)
         print'MISSION ENDED'
         self.IO.setSemaphor()
         self.stop()
         time.sleep(10)
         self._pos.restartMission()
         #while OK():
            #if position.localize():
         return True

    def identifyRoom(self):
        if self.comments:
            print 'Identifying the room..'
            for i in range(0,6):
                self.rotate(60)
                time.sleep(0.1)
        #print'Define orientation'
    def setOrientation(self):
        orientation=self._pos.calculateBestRoute()
        print 'Orientation = ',orientation
        if orientation!=None:
            self.rightBias=orientation
        #else:print ''
        print 'Set orientation bias= ',self.rightBias
        if self.rightBias:
            while self.getRightIR()<200:
                self.goRight()
                time.sleep(0.05)
        else:
            while self.getLeftIR()<200:
                self.goLeft()
                time.sleep(0.05)

       # ######################################################
    # #                   Vision Code                      #
    def Vision(self, OK):
        self.IO.cameraSetResolution('low')
        hasImage=False
        res=0
        sw=False
        swPrev=False
        for i in range(0,4):
            self.IO.cameraGrab()
            img=self.IO.cameraRead()
            self.IO.imshow('window',img)
        time.sleep(1)
        self.waitForVision=False

        while OK():

            start=time.time()
            #if not self.analogInputs[4]:
                #for i in range(0,5):
            self._pos.isStartingPoint()
            self.IO.cameraGrab()
            img=self.IO.cameraRead()
            #If robots identifies the room that is into print the room
            if self._pos.localize(img):
               #If robot starts and does not now where it is
               #if self.currentRoom<>self._pos.getCurrentRoom():
               self._pos.printRoom()

               self.currentRoom==self._pos.getCurrentRoom()
                #self._pos.leftRoom()

            #if img.__class__==numpy.ndarray:
                #hasImage=True
            #         #cv2.imwrite('camera-'+datetime.datetime.now().isoformat()+'.png',img)
            #         self.IO.imshow('window',img)
            #         self.IO.setStatus('flash',cnt=2)
            # if hasImage:
            self.IO.imshow('window',img)

            end=time.time()
            time.sleep(0.05)


    ##################Collision avoidance ##############
    def collision(self):
        """Returns True if robot is close to any object
           Sonar value>20"""
#        if self.getSonar()<30:
#             self.l.append(self.getSonar())# If robot gets stacked go 10 cm backwards and retry
#             if(self.l.count(self.getSonar()) == 35):
#                 print 'Endless loop'
#                 print 'Sonar = ',self.getSonar()
#                 self.coverDistance(distance=0.05,frontwards=False)
#                 self.rotate(degrees=45,direction=(self.getLeftIR()>self.getRightIR()))
#                 self.l.clear()
#                 return False


        if self.getSonar()<25:
            if self.comments:print('Obstacle detected!')
            #if self.getLeftIR()>self._irThreshold:#if obstacle is on the left and in front of you turn 90 degrees right
            if (self.getLeftIR()>self._irThreshold):# or self.hasWallonLeft:
                if self.comments:print 'Obstacle in front and left'
                self.rotate(degrees=45,direction=False)
                #self.hasWallonLeft=True
                return False
            #elif self.getRightIR()>self._irThreshold:#if obstacle is on the left and in front of you turn 90 degrees right
            elif (self.getRightIR()>self._irThreshold):# or self.hasWallonRight:
                if self.comments:print 'obstacle in front and right'
                self.rotate(degrees=45,direction=True)
                #self.hasWallonRight=True
                return False
            else:#if there is an obstacle only in front of you
                if(self.getLeftIR()>self.getRightIR()):#If obstacle is closer to one way turn towards the other
                #################CHANGED########################
                #if(self.rightBias):
                    #self.goRight()
                    ##############TO TEST#####################
                    #self.rotate(degrees=15,direction=False)
                    self.rotate(degrees=15,direction=False)
                else:
                    ##############TO TEST#####################
                    #self.rotate(degrees=15,direction=True)
                    self.rotate(degrees=15,direction=True)
            return False
            #time.sleep(0.05)
        else:#if there is no obstacle in front of the robot

                if self.getLeftIR()>self._irThreshold:#if obstacle is detected on left side, go right
                    if self.comments:print 'Collision on left!'
                    self.goRight()
                    return True
                elif(self.getRightIR()>self._irThreshold):#if obstacle is detected on right side go left
                    if self.comments:print'Collison on right!'
                    self.goLeft()
                    return True
                #if(self.getLeftIR()<=self._irThreshold and self.getRightIR()<=self._irThreshold):#if no obstacles detected on both sides do nothing
        self.findWall()
        return self.followEdges()



    def findWall(self):
        #if self.comments:print' Findwall'
                #Check if there are walls in the sides of the robot
        if self.rightBias:
            if self.getRightIR()>100:
                if self.comments:print 'Has wall on right'
                self.hasWallonRight=True
                self.edge=False
        else:
            if self.getLeftIR()>100:
                if self.comments:print'Has wall on left'
                self.hasWallonLeft=True
                self.edge=False

        if self.edge:
            print 'enter edge'
            self.coverDistance(0.22)
            self.rotate(80,not self.rightBias)
            self.edge=False
        return False
            #if self.hasWallonLeft==False and self.getSonar()>80:
            #    self.rotate(15)
            ###################TEST######################0
    #This mehtod takes for granted we are parallel to a wall
    def followEdges(self):
        #print 'Follow edges'
        if self.rightBias:
#            if self.getRightIR()<300 and self.getRightIR()>200:
#                self.goRight()
#                if self.comments:print 'Lost track of the wall going right'
#                return True
#            #print 'Following to the right'
            if self.getRightIR()<50 and self.hasWallonRight:
                if self.comments:print 'Detected edge on right'
                self.coverDistance(0.30)
                self.rotate(80,False)
                self.hasWallonRight=False
                self.edge=True
        else:
#            if self.getLeftIR()<400 and self.getLeftIR()>200:
#                self.goLeft()
#         #       if self.comments:print 'Lost track of the wall going left'
#                #print 'Following the wall'
#                return  True
            if self.getLeftIR()<50 and self.hasWallonLeft:
                 if self.comments:print 'Detected edge on left'
                 self.coverDistance(0.30)
                 self.rotate(80)
                 self.hasWallonLeft=False
                 self.edge=True
        return False

            #Use the switch to take photographs
            # sw=self.analogInputs[5]
            # if sw!=swPrev and sw:
            #     res=(res+1)%4
            #     if res==0:
            #         self.IO.cameraSetResolution('low')
            #         self.IO.setError('flash',cnt=1)
            #     if res==1:
            #         self.IO.cameraSetResolution('medium')
            #         self.IO.setError('flash',cnt=2)
            #     if res==2:
            #         self.IO.cameraSetResolution('high')
            #         self.IO.setError('flash',cnt=3)
            #     if res==3:
            #         self.IO.cameraSetResolution('full')
            #         self.IO.setError('flash',cnt=4)
            #     time.sleep(0.5)
            # swPrev=sw

            #time.sleep(0.05)


    ########################################################
    #                  Goal methods                        #
    def gotGoal(self):
        """
        :return: True if robot covered given distance
                D= 2*pi*r*wheelSpins/2*gearRatio"""
        return (numpy.pi*0.04/5*self.spins<self.getGoal())
    def getGoal(self):
        """:return: distance to cover
        """
        return self._goal
    def setGoal(self,goal):
        """:param goal: meters to cover
        """
        self._goal=goal
    def calculateDistance(self):
        return numpy.pi*0.04/5*self.spins

    #aristera=gostraight
    ########################################################
    #                   Motion Control                     #
    def goStraight(self):
        #print('Go straight')
        self.IO.setMotors(-100, -100)
    def goLeft(self):
        #print('Go left')
        self.IO.setMotors(100, -100)
        #return [-100, 100]
    def goRight(self):
        #print('Go right')
        self.IO.setMotors(-100, 100)
        #return [100, -100]
    def goBackwards(self):
        #print('Go backwards')
        self.IO.setMotors(100, 100)
        #return [-100, -100]
    def stop(self):
        print('Stop!')
        self.IO.setMotors(0, 0)
        #return[0, 0]
    def rotate(self,degrees=30,direction=True):
        """
        :param degrees:   set degrees of rotation
        :param direction: True=left  ||   False=right
        Rotate by 'degrees' degrees to the left/right
        """

        print 'Rotate ',degrees,' to the ','left 'if direction else 'right'
        self.setGoal(self.distanceToRotate90*degrees/90)
        self.round=self.getHall()
        while (self.gotGoal()):
            if(self.getHall()<>self.round):
                self.spins += 1
                self.round= self.getHall()
            if direction:self.goLeft()
            else: self.goRight()
        self.stop()
        self.spins=0
        #print 'Rotated ', degrees,' degrees to the ','left' if direction else 'right'
    def coverDistance(self,distance=0.2,frontwards=True):
        """
        :param distance: meters
        :param frontwards: True to go frontwards
        :return:

        Move 'distance' in meters frontwards/backwards
        """
        print 'Distance to cover ',distance
        self.setGoal(distance)
        self.round=self.getHall()
        while self.gotGoal():
            if(self.getHall()<>self.round):
                self.spins += 1
                self.round= self.getHall()
            if frontwards:self.goStraight()
            else: self.goBackwards()
        self.stop()
        self.spins=0

    ##########################################################
    #                   Get digital Inputs                   #
    ##              Inputs: 2:Sonar                          #
    ##                      3:LightSensor
    ##                      6:Left IR                        #
    ##                      7:Right IR                       #
    def getSonar(self):
        return self.digitalInputs[0]
    def getFloorLight(self):
        return self.digitalInputs[1]
    def getLeftIR(self):
        return self.digitalInputs[7]
    def getRightIR(self):
        return self.digitalInputs[6]
    #def getWhisker(self):
        #return self.analogInputs[]
    def getHall(self):
        return self.analogInputs[7]
    def getDistanceSensor(self):
        return self.digitalInputs[0]
    #Get analog Inputs
    def getWhisker(self):
        return self.analogInputs[0]


    ##########################################################
    def testSensors(self):
        """ Module outpouts all sensors(analog and logical) data in 2 vectors """
        while True:
            print('digital')
            for i in range(len(self.digitalInputs)):
                print(' %r = %r' %(i,self.digitalInputs[i]))
            print('analog')
            for l in range(len(self.analogInputs)):
                print(' %r = %r' %(l,self.analogInputs[l]))
            time.sleep(0.05)


##############################################################################
    #     #Method to take pictures
    # # This is a callback that will be called repeatedly.
    # # It has its dedicated thread so you can keep block it.
    # def Vision(self, OK):
    #     print 'Vision'
    #     self.IO.cameraSetResolution('low')
    #     hasImage=False
    #     res=0
    #     sw=False
    #     swPrev=False
    #     while OK():
    #         if not self.analogInputs[4]:
    #             print 1
    #             for i in range(0,5):
    #                 self.IO.cameraGrab()
    #             img=self.IO.cameraRead()
    #             if img.__class__==numpy.ndarray:
    #                 hasImage=True
    #                 cv2.imwrite('camera-'+datetime.datetime.now().isoformat()+'.png',img)
    #                 self.IO.imshow('window',img)
    #                 self.IO.setStatus('flash',cnt=2)
    #                 time.sleep(0.05)
    #         if hasImage:
    #             self.IO.imshow('window',img)



            # time.sleep(0.05)

    ################################################################








