import carla
import numpy as np
import random
from .ClientUser import ClientUser

class SimulationVisualization(ClientUser):

    def __init__(self, client):
        super().__init__(client)

        self.tracking = {} # actor id -> tracking config

        self.world.on_tick(self.onTick)

    

    def onTick(self, world_snapshot):
        for actorId in self.tracking:
            actor_snapshot = world_snapshot.find(actorId)
            if actor_snapshot is not None:
                lifetime = self.tracking[actorId]["lifetime"]
                color = self.tracking[actorId]["color"]
                self.drawWalkerBB(actor_snapshot, color=color, lifetime=lifetime)

    #region unit functions

    def getRandomColor(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(0, 100)

        return (r, g, b, a)

    
    def drawPoint(self, location, size=0.1, color=(255,0,0,100), lifetime = 0):
        self.debug.draw_point(location, size, carla.Color(*color),  lifetime)

    def drawBox(self, bb, rotation, thickness=0.1, color=(255,0,0, 100), lifetime = 0):
        self.debug.draw_box(
                    bb,
                    rotation, 
                    thickness, 
                    carla.Color(*color),
                    lifetime)

    def drawTextOnMap(self, location, text, life_time=0):
        self.drawText(
            location=location, 
            text=text, 
            draw_shadow = True,
            color=(0, 0, 0, 0),
            life_time=life_time
        )

    def drawText(self, location, text, draw_shadow=False, color=(255,0,0), life_time=-1.0):
        self.debug.draw_string(
            location, 
            text, 
            draw_shadow,
            carla.Color(*color),
            life_time
            )



    
    
    def draw00(self):
        bb = carla.BoundingBox(
            carla.Location(x=0, y=0, z=0), 
            carla.Vector3D(1,1,1) # assuming all walkers are less than 2 meters in height
        )
        rotation = carla.Rotation(pitch=-90)
        self.drawBox(bb, rotation, thickness=0.1, color=(0, 0, 0, 0))

    def drawWalkerBB(self, walker, thickness=0.1, color=(255,0,0, 100), lifetime = 0):
        bb = self.getWalkerBB(walker)
        rotation = walker.get_transform().rotation
        self.drawBox(bb, rotation, thickness=thickness, color=color, lifetime=lifetime)

    def getWalkerBB(self, walker):
        return carla.BoundingBox(
            walker.get_transform().location, 
            carla.Vector3D(0.5,0.5,2) # assuming all walkers are less than 2 meters in height
        )

    # trajectory

    def trackOnTick(self, actorId, config=None):
        if config is None:
            config = { 'lifetime': 0 }

        if 'color' not in config:
            config['color'] = self.getRandomColor()

        self.tracking[actorId] = config
    

    # some positional information
    def drawSpawnPoints(self):
        spawn_points = self.map.get_spawn_points()
        for point in spawn_points:
            location = point.location
            print(f"spawn_point position ({location.x}, {location.y})")
            self.drawPoint(location=location, size=0.05)


    def drawSpectatorPoint(self):
        spectator = self.world.get_spectator()
        location = spectator.get_location()
        print(f"spectator position ({location.x}, {location.y})")
        drawLocation = carla.Location(location.x, location.y, 0)
        self.drawPoint(location=drawLocation, size=0.5, color=(0, 50, 200))
        self.drawTextOnMap(location=carla.Location(location.x, location.y, 10), text=f"Center ({location.x}, {location.y})")




    

    
