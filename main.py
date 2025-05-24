from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import numpy as np
import random

# Material colors (R, G, B, A)
MATERIALS = {
    "air": (0, 0, 0, 0),
    "stone": (0.5, 0.5, 0.5, 1),
    "water": (0, 0.5, 1, 0.7),
    "grass": (0.2, 0.8, 0.2, 1),
    "crystal": (0.8, 0.2, 0.8, 0.8),
}


class VoxelGridApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Grid settings
        self.grid_size = 16
        self.cube_size = 0.1

        # Camera controls
        self.camera_distance = 5
        self.camera_theta = 45  # Rotation around Y-axis
        self.camera_phi = 30  # Rotation around X-axis
        self.mouse_drag = False
        self.last_mouse_pos = (0, 0)

        # Disable default camera controls
        self.disableMouse()

        # Setup scene
        self.setup_scene()
        self.generate_grid()

        # Input handlers
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        self.accept("mouse1", self.start_drag)
        self.accept("mouse1-up", self.stop_drag)
        self.taskMgr.add(self.update_camera, "update_camera")

    def setup_scene(self):
        """Initialize lighting and background"""
        self.setBackgroundColor(0.1, 0.1, 0.1)
        self.render.setShaderAuto()

        # Add lights
        ambient_light = AmbientLight("ambient")
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        directional_light = DirectionalLight("directional")
        directional_light.setDirection((-1, -1, -1))
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))
        self.render.setLight(self.render.attachNewNode(directional_light))

    def generate_grid(self, time=1.5):
        """Create voxel grid from your script"""
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    # Replace with your script logic
                    r = x * 0.5 + np.sin(time) * 3
                    mat = "crystal" if y < r else "air"

                    if mat != "air":
                        self.create_cube(x, y, z, mat)

    def create_cube(self, x, y, z, material):
        """Add a colored cube to the scene"""
        cube = self.loader.loadModel("models/box")
        cube.setScale(self.cube_size)

        # Position cube (centered at origin)
        offset = (self.grid_size - 1) * self.cube_size / 2
        cube.setPos(
            x * self.cube_size - offset,
            y * self.cube_size - offset,
            z * self.cube_size - offset,
        )

        # Set material color
        color = MATERIALS.get(material, (1, 0, 0, 1))
        cube.setColor(color[0], color[1], color[2], color[3])

        cube.reparentTo(self.render)

    def start_drag(self):
        self.mouse_drag = True
        self.last_mouse_pos = (
            self.mouseWatcherNode.getMouseX(),
            self.mouseWatcherNode.getMouseY(),
        )

    def stop_drag(self):
        self.mouse_drag = False

    def zoom(self, direction):
        self.camera_distance = max(1, min(10, self.camera_distance - direction * 0.5))

    def update_camera(self, task):
        if self.mouse_drag:
            mx, my = (
                self.mouseWatcherNode.getMouseX(),
                self.mouseWatcherNode.getMouseY(),
            )
            dx = mx - self.last_mouse_pos[0]
            dy = my - self.last_mouse_pos[1]

            self.camera_theta -= dx * 100
            self.camera_phi = max(-80, min(80, self.camera_phi + dy * 100))

            self.last_mouse_pos = (mx, my)

        # Update camera position (spherical coordinates)
        theta_rad = self.camera_theta * np.pi / 180
        phi_rad = self.camera_phi * np.pi / 180

        cam_x = self.camera_distance * np.sin(theta_rad) * np.cos(phi_rad)
        cam_y = self.camera_distance * np.cos(theta_rad) * np.cos(phi_rad)
        cam_z = self.camera_distance * np.sin(phi_rad)

        self.camera.setPos(cam_x, cam_y, cam_z)
        self.camera.lookAt(0, 0, 0)

        return Task.cont


if __name__ == "__main__":
    app = VoxelGridApp()
    app.run()
