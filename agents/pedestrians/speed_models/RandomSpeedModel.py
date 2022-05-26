from .SpeedModel import SpeedModel
import random

class RandomSpeedModel(SpeedModel):
    
    def initialize(self):
        random_adjustment = random.uniform(0.5, 1.5)
        self._desiredSpeed = self.internalFactors["desired_speed"] * random_adjustment
        self._minSpeed = self.internalFactors["min_crossing_speed"] * 10 * random_adjustment
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * 10 * random_adjustment
        pass