# Ryan Cai
# xcai30@ucsc.edu
# 4/19/2022
# basic script to spawn some actors in CARLA
import carla
import random

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
pedestrians = bplib.filter('walker.pedestrian.0001')
walker_transform = carla.Transform()
for i in range(10):
        loc = world.get_random_location_from_navigation()
        # locations.append(loc)
        walker_transform.location = loc
        world.try_spawn_actor(random.choice(pedestrians), walker_transform)

# get spectator from world
camera = world.get_spectator()
camera.set_transform(random.choice(spawn_points))


