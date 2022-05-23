from .SpeedModel import SpeedChangeModel

class AggressiveSpeedModel(SpeedChangeModel):

    USAIN_BOLT = 12.27 # m/s

    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * 3.25
        self._minSpeed = self.internalFactors["min_crossing_speed"] * 3.25
        self._maxSpeed = USAIN_BOLT
        
        pass