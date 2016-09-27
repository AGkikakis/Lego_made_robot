import  colorIdentification
from math import fabs
import numpy as np
""" Contains the potision of the robot
"""
class Position:

    #       ROOM E          #           ROOM F      #
    #################################################
    #                       #              -------- #
    #                       #              |strt 2| #
    #      ###              #              -------- #
    #      ###            ###                       #
    #                                   #############
    #           #####                               #
    #           #                                   # R
    #############                                   # O
# R #                   ######                      # O
# O #                  ########                     # M
# O #                  ########                     #
# M #                   ######                      # D
#   #                               #################
# C #                               #               #
    #                             ###               #
    #                                               #
    ###########                                     #
    #                                    ###        #
    #                       ####         ###        #
    #  --------             #                       #
    #  |strt 1|             #                       #
    #  --------             #                       #
    #################################################
    #       ROOM A          #       ROOM B          #


    def __init__(self,IO,roomtoreach,startingRoom=None,firstBase=False):
        print('Initializing Position')
        #self.position=self._startingPoint
        #Terminator finishes its mission in the appointed room
        ##################################################
        ##                 color label                  ##
        ## 0 = blue   1 = red    2 = yellow   3 = black ##
        ## 4 = white  5 = green  6 = orange             ##
        ## 7 = light green                              ##
        ##################################################
        self.BLUE=0
        self.RED=1
        self.YELLOW=2
        self.BLACK=3
        self.WHITE=4
        self.GREEN=5
        self.ORANGE=6
        self.LIGHT_GREEN=7
        self.BASE=8
    ##########################################################################
    ##                        room identification                           ##
    ##  Room A = blue and black                                             ##
    ##  Room B = yellow and green || orange and green || yellow and orange  ##
    ##  Room C = green and white (or only green)                            ##
    ##  Room D = blue, yellow and black                                     ##
    ##  Room E = red and blue || red, blue and black || red and black       ##
    ##  Room F = green and black                                            ##
    ##########################################################################
        #Initialilze module for object identification using color histograms
        self.colorIdent=colorIdentification.ColorIdentification()
        #True if terminator starts from a base
        self.startedOnBase=True
        ################All inputs########################
        self.IO=IO
        self.digitalInputs=self.IO.getSensors()
        self.analogInputs=self.IO.getInputs()
        ###################Room Parameters#################
        #List containing all objects detected in room
        self.objectsDetcetedInRoom=list()
        #List of arrays containing the object every room has
        self.room_A=[[ self.BLUE, self.BASE],[self.BLUE,self.BLACK,self.BASE]]
        self.room_B=[[self.YELLOW,self.GREEN],[self.GREEN,self.ORANGE],[self.YELLOW,self.ORANGE],[self.YELLOW,self.GREEN,self.ORANGE],[self.ORANGE]]
        self.room_C=[[self.WHITE,self.GREEN],[self.WHITE],[self.WHITE,self.LIGHT_GREEN],[self.GREEN,self.LIGHT_GREEN],[self.LIGHT_GREEN]]
        #Problem confusing with base
        self.room_D=[[ self.BLUE,self.YELLOW,self.BLACK],[self.YELLOW,self.BLACK],[self.BLUE,self.YELLOW]]
        self.room_E=[[self.RED],[self.BLUE,self.RED],[self.RED,self.BLACK],[self.BLUE,self.RED,self.BLACK]]
        self.room_F=[[ self.GREEN,self.BASE],[self.BLACK,self.GREEN],[self.BLACK,self.GREEN,self.BASE]]
        self.allRooms=[self.room_A,self.room_B,self.room_C,self.room_D,self.room_E,self.room_F]
        #Current room=None
        self._setCurrentRoom()
        self.routeMap=[self.room_A,self.room_B,self.room_D,self.room_F,self.room_E,self.room_C]

        self.mission=self.roomToReach(roomtoreach)

        #################Mission Parameters#################
        #Boolean to denote if mission has ended
        self.missionEnded=False
        #Terminator just started its mission
        self.justStartedMission=True
        #Checks if terminator starts its mission from a base
        #self.startedOnBase=self.isStartingPoint()


        #############################################################

    def localize(self,img):
        """
        Attempts to identify the room where the robot is
        :param img:
        :return:
        """
        objectCheck=self.colorIdent.identifyObject(img)
        #If method returns empty list do nothing
        if len(objectCheck)==0:
            return self.identifyRoom()
        else:
            for i in objectCheck:
                if not (i in self.objectsDetcetedInRoom):#if object not already on list add it
                    self.addObject(i)
        self.areObjectsValid()
        return self.identifyRoom()

    def identifyRoom(self):
        """Iterates each rooms objects given the odjects identified, to determine if the room is identified"""
        #print 'identify Room'
        success=False
        if len(self.objectsDetcetedInRoom)< 1:
            return success
        #print 'List ',self.objectsDetcetedInRoom
        #print len(self.objectsDetcetedInRoom)
        obj = self.objectsDetcetedInRoom
        obj.sort()
        print obj
        for i in range(len(self.allRooms)):
            print self.allRooms[i]
            if obj in self.allRooms[i]:
                success=True
                #print 'room ',i ,' contains ', obj
                #print 'Found ',obj
                self._setCurrentRoom(self.allRooms[i])
                self.flash(i)
        if self.getCurrentRoom()==self.mission:#If robot reaches room in mission, then mission ended
            self.missionEnded=True
            print 'Mission'
        return success
    def leftRoom(self):
        """Robot leaves room"""
        print 'Robot left Room'
        self.objectsDetcetedInRoom=list()
        self._setCurrentRoom()
    def getCurrentRoom(self):
        """Returns the room the robot is currently in"""
        return self._currentRoom
    def _setCurrentRoom(self,room=None):
        """Set the room the robot is"""
        self._currentRoom=room
    def flash(self,times,speed=10):
        """ Flashes 'time' times"""
        self.IO.setStatus('flash',speed,times,0)
        self.IO.setError('flash',speed,times,1)
    def printRoom(self):
        room={
            0:"Room A",
            1:"Room B",
            2:"Room C",
            3:"Room D",
            4:"Room E",
            5:"Room F"
        }
        print "Robot is in ", room.get(self.allRooms.index(self._currentRoom),'Robot cannot identify its location')

    #########################################################
    def addObject(self,obj):
        print 'Object added ', obj
        self.objectsDetcetedInRoom.append(obj)

    def roomToReach(self,roomtoreach):
        room={
            'A':self.room_A,
            'B':self.room_B,
            'C':self.room_C,
            'D':self.room_D,
            'E':self.room_E,
            'F':self.room_F
        }
        return room.get(roomtoreach,None)
    def indexOfRoomToReach(self,roomtoreach):
        room={
            'A':0,
            'B':1,
            'C':2,
            'D':3,
            'E':4,
            'F':5
        }
        return room.get(roomtoreach,'Cannot identify target Room')

    def calculateBestRoute(self):
        print 'Calculatebestroute'
        if self._currentRoom==None:
            return None
        else:
            curRoomInd=self.routeMap.index(self._currentRoom)
            missionRoomInd=self.routeMap.index(self.mission)


            if fabs(missionRoomInd-curRoomInd)<=3:
                if missionRoomInd>curRoomInd:
                    print 'CalculateBestroute sayes go Right'
                    return True
                else:
                    print 'CalculateBestroute sayes go Left'
                    return False
            else:
                if missionRoomInd>curRoomInd:
                    print 'CalculateBestroute sayes go Left'
                    return False
                else:
                    print 'CalculateBestroute sayes go Right'
                    return True


    def areObjectsValid(self):
        """if list contains more than 3 objects and they are not room E objects robot has identified objects from previous
        room without identifing it"""
        if len(self.objectsDetcetedInRoom)>2:
            if len(self.objectsDetcetedInRoom)==3:
                obj = self.objectsDetcetedInRoom
                obj.sort()
                if (obj in self.allRooms[4]) or (obj in self.allRooms[3]) or (obj in self.allRooms[0] or (obj in self.allRooms[5])):
                    return True
            #delete previous objects and keep last object
            #lastObj=self.objectsDetcetedInRoom[0]
            print 'Combination of objects does not exist, robot couldnt adentify previous room and moved on'
            #print'Keeping last object :', lastObj

            self.leftRoom()
            #self.addObject(lastObj)
        return False

    #########################################################
    def isStartingPoint(self):
        """Returns True if robot is on starting base or False if it is NOT
            Also signals the end of the mission if robot visits a base for the second time"""
        if(self.getFloorLight()<=70):
            #print 'Robot is on base'
            #self.addObject(self.BASE)
            #If the robot starts on base, do nothing until it leaves
            #If the robot has already left base once then it has returned
            #if not self.justStartedMission:
                #print 'Robot returned to base'
                #self.missionEnded=True
            if not(self.BASE in self.objectsDetcetedInRoom):
                    self.addObject(self.BASE)
                    self.areObjectsValid()
                    self.identifyRoom()
            return True
        else:
            self.justStartedMission=False
            return False
    def isMissionEnded(self):
        #time.sleep(5)
        return self.missionEnded
    def restartMission(self):
        self.missionEnded=False
        self.leftRoom()
        #self.startingPoint=True

    ##########################################################
    #get AnalogInputs
    def getSonar(self):
        return self.digitalInputs[0]
    def getFloorLight(self):
        return self.digitalInputs[1]
    #def getWhisker(self):
        #return self.analogInputs[]
    def getHall(self):
        return self.digitalInputs[7]
    def getDistanceSensor(self):
        return self.digitalInputs[0]

    def getObjDetinRoom(self):
        if len(self.objectsDetcetedInRoom)<=1:
            return self.objectsDetcetedInRoom
        return [item for sublist in self.objectsDetcetedInRoom for item in sublist]