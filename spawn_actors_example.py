# Ryan Cai
# Betros
# Andrei
# xcai30@ucsc.edu
# 4/19/2022
# basic script to spawn some actors in CARLA
import carla
import random
import sys
from time import sleep

# connect to client
ghost = '127.0.0.1'
gport = 2000

client = carla.Client(ghost, gport)
client.set_timeout(20.0)

#print("server ver: ", client.get_server_version())
#print("client ver: ", client.get_client_version())

# get all available maps from client
print(client.get_available_maps())

# load world and get map
world = client.load_world('Town01')
map = world.get_map()

# get points from map
spawn_points = map.get_spawn_points()

# get blueprint
bplib = world.get_blueprint_library()

# get a audi a2 blueprint
vehicles = bplib.filter('vehicle.audi.a2')

# spawn vehicle at specific point
for i in range(3):
        world.spawn_actor(random.choice(vehicles), random.choice(spawn_points))

# get pedestrian bp
pedestrians = bplib.filter('walker.pedestrian*') # walker.pedestrian.0001
walker_transform = carla.Transform() #default position of a pedestrean 

for i in range(10):
        loc = world.get_random_location_from_navigation()
        # locations.append(loc)
        walker_transform.location = loc # # changing ped to random possition 
        p = world.try_spawn_actor(random.choice(pedestrians), walker_transform) # creating a single actor
        print(p)
        sys.stdout.flush() #print immediately(happned after ctr+c)
        if p:              #if succ stop creating other peds
                break
        
# get spectator from world
camera = world.get_spectator() # 


camera_transform = carla.Transform(
        carla.Location(loc.x, loc.y, loc.z + 20), # 20 altitude
        carla.Rotation(-90.0, 0.0, 0.0), # face 90 degree down
)
camera.set_transform(camera_transform)

walker_controller_bp = bplib.find('controller.ai.walker')
ai_controller = world.spawn_actor(
        walker_controller_bp,
        carla.Transform(), p)

ai_controller.start()
ai_controller.go_to_location(world.get_random_location_from_navigation())
ai_controller.set_max_speed(1 + random.random())


for i in range(20):
        print("Pedestrian is at:", p.get_location())
        sleep(0.5)
        # camera.set_transform(sensor.get_transform())
        # p_loc = p.get_location()
        # walker_transform.location = carla.Location(p_loc.x, p_loc.y, p_loc.z + 10)
        # walker_transform.rotation = carla.Rotation(-90.0, 0.0, 0.0)
        # camera.set_transform(walker_transform)






