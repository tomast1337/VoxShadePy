from vpython import *
import numpy as np
from interpreter import (
    evaluate_voxel_shader,
)


program = """
color = air;
if (sin(time) * 4 + 4 > 1) {
    color = ice;
}
"""


materials = {
    "air": {"color": vector(0, 0, 0), "opacity": 0.0},
    "stone": {"color": vector(0.5, 0.5, 0.5), "opacity": 1.0},
    "water": {"color": vector(0.2, 0.4, 0.8), "opacity": 0.8},
    "grass": {"color": vector(0.1, 0.8, 0.1), "opacity": 0.0},
    "crystal": {"color": vector(1, 1, 1), "opacity": 0.8},
    "sand": {"color": vector(0.9, 0.8, 0.6), "opacity": 0.0},
    "wood": {"color": vector(0.6, 0.3, 0.1), "opacity": 0.0},
    "metal": {"color": vector(0.7, 0.7, 0.7), "opacity": 0.0},
    "lava": {"color": vector(1, 0.2, 0), "opacity": 0.0},
    "ice": {"color": vector(0.8, 0.9, 1), "opacity": 0.7},
    "dirt": {"color": vector(0.4, 0.3, 0.2), "opacity": 0.0},
    "snow": {"color": vector(1, 1, 1), "opacity": 0.0},
    "cloud": {"color": vector(0.9, 0.9, 0.9), "opacity": 0.5},
    "glass": {"color": vector(0.8, 0.8, 0.8), "opacity": 0.0},
    "brick": {"color": vector(0.8, 0.2, 0.2), "opacity": 0.0},
    "obsidian": {"color": vector(0.1, 0.1, 0.1), "opacity": 0.0},
}

SIZE = 8
CENTER = vector(SIZE / 2 - 0.5, SIZE / 2 - 0.5, SIZE / 2 - 0.5)
time = 0

# Scene setup
scene = canvas(
    title="8×8×8 Cube Pile - Dynamic Shader",
    width=800,
    height=600,
    background=color.white,
    up=vector(0, 1, 0),
    center=CENTER,
    forward=vector(-1, -1, -1),
)
scene.camera.pos = vector(10, 10, 10)
scene.camera.pos = vector(10, 10, 10)  # Position camera further away

cubes = []
for x in range(SIZE):
    for y in range(SIZE):
        for z in range(SIZE):
            result = evaluate_voxel_shader(x=x, y=y, z=z, time=time, program=program)
            material = materials.get(result, {"color": vector(1, 1, 1), "opacity": 0.8})
            if material["opacity"] > 0.0:
                cubes.append(
                    box(
                        pos=vector(x, y, z),
                        size=vector(0.9, 0.9, 0.9),
                        color=material["color"],
                        opacity=material["opacity"],
                        shininess=0.6,
                        # Store original position for rotation reference
                        _original_pos=vector(x, y, z),
                    )
                )
# Add some lighting to enhance the 3D effect
distant_light(direction=vector(1, 1, 1), color=color.white)
distant_light(direction=vector(-1, -1, -1), color=color.white)

# Keep the program running
while True:
    rate(30)
    time += 0.1  # Increment time for animations

    # Update cubes based on shader
    for cube in cubes:
        # Get original position
        x, y, z = cube._original_pos.x, cube._original_pos.y, cube._original_pos.z

        # Re-evaluate shader with current time
        result = evaluate_voxel_shader(x=x, y=y, z=z, time=time, program=program)
        material = materials.get(result, {"color": vector(1, 1, 1), "opacity": 0.8})

        # Update cube properties
        cube.color = material["color"]
        cube.opacity = material["opacity"]

        # Rotate around center
        cube.rotate(angle=0.01, axis=vector(0, 1, 0), origin=CENTER)
