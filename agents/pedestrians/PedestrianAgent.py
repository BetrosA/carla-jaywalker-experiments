from msilib.schema import Error
from random import random
import numpy as np
import time
import carla
import logging
from .InfoAgent import InfoAgent
from lib import SimulationVisualization
from .planner.PedestrianPlanner import PedestrianPlanner
from .PedState import PedState
from .StateTransitionManager import StateTransitionManager
from typing import Dict
from .PedUtils import PedUtils


class PedestrianAgent(InfoAgent):
    
    def __init__(self, walker, time_delta, desired_speed=1.5, visualizer=None, config=None):
        """
        Initialization the agent paramters, the local and the global planner.

            :param walker: actor to apply to agent logic onto
            :param desired_speed: speed (in m/s) at which the vehicle will move range is (0.7-5.7) Pedestrian acceleration and speeds, 2012
            :param opt_dict: dictionary in case some of its parameters want to be changed.
                This also applies to parameters related to the LocalPlanner.
        """

        self.name = f"PedestrianAgent #{walker.id}"
        self.state = PedState.INITALIZING
        super().__init__(self.name, walker, desired_speed=desired_speed, config=config)
        self._world = self._walker.get_world()
        self._map = self._world.get_map()

        self.skip_ticks = 20 # takes about 10 ticks for the vehicle to start
        self.time_delta = time_delta
        self.tickCounter = 0

        self.visualizer = visualizer


        self._last_jumped = time.time_ns()

        self.collisionSensor = None
        self.obstacleDetector = None

        self.visualizationForceLocation = None
        if config is not None:
            if "visualizationForceLocation" in config:
                self.visualizationForceLocation = config["visualizationForceLocation"]

        self.visualizationInfoLocation = None
        if config is not None:
            if "visualizationInfoLocation" in config:
                self.visualizationInfoLocation = config["visualizationInfoLocation"]
                
        # config parameters

    @property
    def world(self):
        return self._world

    @property
    def map(self):
        return self._map

    @property
    def actorManager(self):
        return self._localPlanner.actorManager
    @property
    def obstacleManager(self):
        return self._localPlanner.obstacleManager
  
    def getAvailableTimeGapWithClosestVehicle(self):
        # time gap = time taken for the oncoming vehicle to reach + time to cross the lane.
        # TODO assuming vehicle driving in agent's nearest lane 
        # TODO Assuming pedestrian will cross at desired speed.
        TTC = self.actorManager.pedTTCNearestOncomingVehicle()
        self.logger.info(f"TTC = {TTC} seconds")

        if TTC is None:
            return None


        TTX = PedUtils.timeToCrossNearestLane(self.map, self.location, self._localPlanner.getDestinationModel().getDesiredSpeed())

        TG = self.addError(TTC)

        self.logger.info(f"TG (Time gap) = {TG} seconds")

        # if TG > TTX:
        #     # positive oncoming vehicle force
        # else:
        #     # negative oncoming vehicle force.

        return TG

    def addError(self, TTC):
        # TODO better modeling than a noise, error = f(distance, speed, occlusions, etc)"
        noiseFactor = np.random.uniform(0.5, 1.5)
        return TTC * noiseFactor # TODO error modeling in Gap

    #region states

    def isCrossing(self):
        if self.state == PedState.CROSSING:
            return True
        return False

    def isWaiting(self):
        if self.state == PedState.WAITING:
            return True
        return False

    def isFinished(self):
        if self.state == PedState.FINISHED:
            return True
        return False

    # region visualization
    def visualiseState(self):
        self.visualizer.drawPedState(self.state, self.walker, life_time=0.1)

    

    def visualiseForces(self):
        forces = self._localPlanner.modelForces

        visualizationForceLocation = self.location + carla.Location(x=10)
        if self.visualizationForceLocation is not None:
            visualizationForceLocation = self.visualizationForceLocation

        visualizationInfoLocation = self.location + carla.Location(x=10)
        if self.visualizationInfoLocation is not None:
            visualizationInfoLocation = self.visualizationInfoLocation

        self.visualizer.visualizeForces(
            self.name, 
            forces = forces, 
            forceCenter = visualizationForceLocation, 
            infoCenter = visualizationInfoLocation, 
            life_time=0.15
            )
    #endregion
    

    def isInitializing(self): 
        if self.skip_ticks == 0:
            return False

        self.tickCounter += 1
        if self.tickCounter == self.skip_ticks:
            # time to wait
            StateTransitionManager.changeAgentState(f"{self.name}.isInitializing", self, PedState.WAITING)

        if self.tickCounter >= self.skip_ticks:
            return False

        return True

    def reset(self, newStartPoint:carla.Location=None):
        self.logger.info(f"Resetting")
        if newStartPoint is not None:
            self._walker.set_location(newStartPoint)

        self.tickCounter = 0
        StateTransitionManager.changeAgentState(f"{self.name}.isInitializing", self, PedState.INITALIZING)
        pass


    def printLocations(self):
        print("Agent location", self._walker.get_location())
        print("Collision location", self.collisionSensor.get_location())
        print("Obstacle detector location", self.obstacleDetector.get_location())

    def calculateControl(self):
        if self.destination is None:
            raise Error("Destination is none")

        if self.isInitializing():
            self.logger.info(f"Pedestrian is initializing.")
            self.visualiseState()
            return self._localPlanner.getStopControl()
        
 
        location = self.feetLocation
        direction = self._localPlanner.getDesiredDirection()
        self.visualizer.drawDirection(location, direction, life_time=0.1)
        # speed = self.calculateNextSpeed(direction)


        self.climbSidewalkIfNeeded()

        control = self._localPlanner.calculateNextControl()

        self.visualiseState()
        self.visualiseForces()

        return control


    # def calculateNextSpeed(self, direction):

    #     # TODO make a smooth transition
    #     # oldControl = self._walker.get_control()
    #     # currentSpeed = oldControl.speed
    #     # nextSpeed = max()
    #     return self.desired_speed



    #region sidewalk

    def canClimbSideWalk(self):

        if self.isFinished():
            return False

        if self.timeSinceLastJumpMS() < 1000:
            return False

        distance = self.distanceToNextSideWalk() 
        if distance is None:
            self.logger.warn(f"Distance to sidewalk is none!")

            return False

        self.logger.info(f"current distance to sidewalk is {distance}")
        distance -= self.getOldSpeed() * self.time_delta
        self.logger.info(f"after tick distance to sidewalk is {distance}")

        walkerSpeed = self.getOldSpeed()

        # if distance < walkerSpeed * 2 and distance > walkerSpeed:
        # if distance < 0.2 and distance > 0.1:
        if distance < 0.2:
            self.logger.info(f"after tick distance to sidewalk is {distance}. Can jump")
            return True
        return False

    def updateJumped(self):
        self._last_jumped = time.time_ns()

    def timeSinceLastJumpMS(self):
        diff = (time.time_ns() - self._last_jumped) // 1_000_000 
        return diff

    def climbSidewalkIfNeeded(self):

        location = self.feetLocation

        if self.canClimbSideWalk():
            self.updateJumped()
            self.logger.info(f"{self.name} climbing up a sidewalk.")
            # self._walker.add_force(carla.Vector3D(0, 0, 10))
            # velocity = self.getOldVelocity() # sometimes old velocity is too low due to collision with the sidewalk..
            
            velocity = self.speedToVelocity(self.desired_speed)

            self._walker.set_location(
                carla.Location(
                    location.x + velocity.x * self.time_delta * 5,
                    location.y + velocity.y * self.time_delta * 5,
                    location.z + 0.5
            ))

    def getObstaclesToDistance(self):
        actorLocation = self._walker.get_location()
        actorXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.05)
        destinationXYLocation = carla.Location(x = self.destination.x, y = self.destination.y, z=0.05)
        labeledObjects = self._world.cast_ray(actorXYLocation, destinationXYLocation)
        # for lb in labeledObjects:
        #     print(f"Labeled point location {lb.location} and semantic {lb.label} distance {actorLocation.distance(lb.location)}")
        return labeledObjects
    
    def distanceToNextSideWalk(self):
        actorLocation = self._walker.get_location()
        # actorXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.)
        labeledObjects = self.getObstaclesToDistance()
        for lb in labeledObjects:
            if lb.label == carla.CityObjectLabel.Sidewalks:
                if self.visualizer is not None:
                    self.visualizer.drawPoint(carla.Location(lb.location.x, lb.location.y, 1.0), color=(0, 0, 255), life_time=1.0)
                # sidewalkXYLocation = carla.Location(x = lb.location.x, y = lb.location.y, z=0.)
                # distance = actorXYLocation.distance_2d(sidewalkXYLocation)
                distance = actorLocation.distance_2d(lb.location)
                self.logger.info(f"Sidewalk location {lb.location} and semantic {lb.label} XY distance {distance}")
                return distance
        return None

    #endregion
    #region sensor handlers

    def handleWalkerCollision(self, data):
        if self.isSidewalk(data.other_actor):
            self.logger.info(f"{self.name} hits a sidewalk")
        else:
            self.logger.info(f"{self.name} hits a non-sidewalk")


    def handWalkerObstacles(self, data):
        # self.logger.info(f"{self.name} sees a obstackle {data.distance}m away with semantic tag {data.other_actor.semantic_tags}")
        # self.logger.info("semantic tag", data.other_actor.semantic_tags)
        # if self.isSidewalk(data.other_actor):

        #     if data.distance < 0.1:
        #         self.logger.info(f"{self.name} is on a sidewalk {data.distance}m away")
        #     else:
        #         self.logger.info(f"{self.name} sees a obstackle {data.distance}m away")

        #     # self._needJump = True
        return
    
    def isSidewalk(self, actor):
        if 8 in actor.semantic_tags:
            return True
        return False

    #endregion



    