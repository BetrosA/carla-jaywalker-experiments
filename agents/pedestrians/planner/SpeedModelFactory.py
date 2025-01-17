from random import Random
from agents.pedestrians.factors import InternalFactors
from agents.pedestrians.speed_models import AggresiveSpeedModel
from agents.pedestrians.speed_models.RandomSpeedModel import RandomSpeedModel
from lib import ActorManager, ObstacleManager
from ..speed_models import *

class SpeedModelFactory:

    modelNameMap = {
        "static": StaticSpeedModel,
        "random": RandomSpeedModel,
        "aggresive": AggresiveSpeedModel,
        "relaxation": RelaxationSpeedModel
    }

    @staticmethod
    def createSpeedModel(name, agent: any,  actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors):
        if name in SpeedModelFactory.modelNameMap:
            return SpeedModelFactory.modelNameMap[name](
                agent=agent,
                actorManager=actorManager,
                obstacleManager=obstacleManager,
                internalFactors=internalFactors
            )
        return None

