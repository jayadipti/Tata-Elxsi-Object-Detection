import carla
import time
import math

def calculate_distance(location1, location2):
    dx = location1.x - location2.x
    dy = location1.y - location2.y
    dz = location1.z - location2.z
    return math.sqrt(dx**2 + dy**2 + dz**2)


def detect_objects(image, ego_vehicle, npc_vehicles, fcw_distance_threshold=10.0):
    ego_location = ego_vehicle.get_location()
    
    for npc in npc_vehicles:
        npc_location = npc.get_location()
        distance = calculate_distance(ego_location, npc_location)

        if distance <= fcw_distance_threshold:
            print(f"Warning! Potential collision detected with {npc.type_id} at distance: {distance:.2f} meters.")


# Function to handle collision events
def collision_event(event):
    print(f"Collision detected! Impact details: {event}")


# Main CARLA simulation
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)

world = client.get_world()

# Blueprint library
blueprint_library = world.get_blueprint_library()

try:
    # Step 1: Spawn Ego Vehicle
    vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]
    spawn_point = world.get_map().get_spawn_points()[0]
    ego_vehicle = world.spawn_actor(vehicle_bp, spawn_point)
    ego_vehicle.set_autopilot(True)  # Enable autopilot for ego vehicle
    print("Ego vehicle spawned.")

    # Step 2: Attach Sensors to Ego Vehicle
    # Collision sensor
    collision_bp = blueprint_library.find('sensor.other.collision')
    collision_sensor = world.spawn_actor(collision_bp, carla.Transform(), attach_to=ego_vehicle)
    collision_sensor.listen(lambda event: collision_event(event))
    print("Collision sensor attached.")

    # Camera sensor for object detection
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '90')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera_sensor = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
    print("Camera sensor attached.")

    # Step 3: Spawn NPC Vehicles
    npc_vehicles = []
    spawn_points = world.get_map().get_spawn_points()
    for i in range(5):  # Spawn 5 NPC vehicles
        if i < len(spawn_points):
            npc_vehicle_bp = blueprint_library.filter('vehicle.audi.a2')[0]
            npc_vehicle = world.spawn_actor(npc_vehicle_bp, spawn_points[i])
            npc_vehicle.set_autopilot(True)  # Enable autopilot for NPCs
            npc_vehicles.append(npc_vehicle)
    print(f"{len(npc_vehicles)} NPC vehicles spawned.")

    camera_sensor.listen(lambda image: detect_objects(image, ego_vehicle, npc_vehicles, fcw_distance_threshold=15.0))

    # Simulation runtime
    time.sleep(20)  # Run simulation for 20 seconds

finally:
    print("Cleaning up actors...")
    if camera_sensor.is_alive:
        camera_sensor.stop()
        camera_sensor.destroy()

    if collision_sensor.is_alive:
        collision_sensor.stop()
        collision_sensor.destroy()

    if ego_vehicle.is_alive:
        ego_vehicle.destroy()

    for npc in npc_vehicles:
        if npc.is_alive:
            npc.destroy()

    print("Simulation ended.")
