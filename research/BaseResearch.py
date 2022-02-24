import carla
import os
from lib import ClientUser, LoggerFactory, MapManager, MapNames, SimulationVisualization
from .SimulationMode import SimulationMode




class BaseResearch(ClientUser):
    def __init__(self, name, client: carla.Client, mapName, logLevel, outputDir:str = "logs", simulationMode = SimulationMode.ASYNCHRONOUS) -> None:
        super().__init__(client)
        logPath = os.path.join(outputDir, f"{name}.log")
        self.logger = LoggerFactory.getBaseLogger(name, defaultLevel=logLevel, file=logPath)

        # doing it before loading the world for physics determinism

        self.simulationMode = simulationMode
        if simulationMode == SimulationMode.ASYNCHRONOUS:
            self.initWorldSettingsAsynchronousMode()
        else:
            self.initWorldSettingsSynchronousMode()

        self.mapManager = MapManager(client)
        self.mapManager.load(mapName)

        self.visualizer = SimulationVisualization(self.client, self.mapManager)

        
        # self.initVisualizer()

        pass


    def initWorldSettingsAsynchronousMode(self):
        time_delta = 0.007
        settings = self.world.get_settings()
        settings.substepping = False
        settings.fixed_delta_seconds = time_delta
        self.world.apply_settings(settings)
        pass

    def initWorldSettingsSynchronousMode(self):
        time_delta = 0.05
        settings = self.world.get_settings()
        # settings.substepping = False # https://carla.readthedocs.io/en/latest/python_api/#carlaworldsettings
        settings.synchronous_mode = True # Enables synchronous mode
        settings.fixed_delta_seconds = time_delta # Sets fixed time step
        self.world.apply_settings(settings)
        pass

    
    def initVisualizer(self):
        self.visualizer.drawSpawnPoints()
        self.visualizer.drawSpectatorPoint()
        self.visualizer.drawAllWaypoints(life_time=1.0)
        pass

    