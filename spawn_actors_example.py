# 4/13/2022
# Created by: Ryan Cai
import carla
import random

# connect to client
ghost = '127.0.0.1'
gport = 2000

client = carla.Client(ghost, gport)
client.set_timeout(10.0)

print("server ver: ", client.get_server_version)
print("client ver: ", client.get_client_version)

# get all available maps from client
print(client.get_available_maps())

# load world and get map
world = client.load_world('circle_t_junctions')
map = world.get_map


# get points from map
spawn_points = map.get_spawn_points()
spawn_point = spawn_points[0]

for point in spawn_points:
        print(f"point: ({point.location.x,}, {point.location.y})")
        print(f"rotation: ({point.rotation.pitch}, {point.rotation.yaw}, {point.rotation.roll})")

# get blueprint
bplib = world.get_blueprint_library()

# get a audi a2 blueprint
vehicles = bplib.filter('vehicle.audi.a2')
vbp = vehicles[0]

# spawn vehicle at specific point
world.spawn_actor(vbp, random(spawn_points))

# get a pedestrian bp
pedestrians = bplib.filter('walker.pedestrian.0001')
pbp = pedestrians[0]
world.spawn_actor(pbp, random(spawn_points))

# get a camera and attach to a pedestrian
cameras = bplib.filter('sensor.camera.rgb')
cbp = cameras[0]
world.spawn_actor(cbp, random(spawn_points), attach_to=pbp.id)

