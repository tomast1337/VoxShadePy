import dearpygui.dearpygui as dpg
from math import sin
from interpreter import run  # Assuming you have this module for running scripts

# Materials and their colors
MATERIALS = {
    "air": (0, 0, 0, 0),  # Transparent (won't be rendered)
    "stone": (0.5, 0.5, 0.5, 1),  # Gray
    "water": (0, 0, 1, 0.7),  # Blue with some transparency
    "grass": (0, 0.8, 0, 1),  # Green
    "crystal": (0.8, 0.2, 0.8, 0.8),  # Purple with some transparency
}


def generate_grid(n=16, time=1.5):
    script = """
    r = x * 0.5 + sin(time) * 3;
    if y < r {
      return crystal;
    }
    return air;
    """

    grid = []
    for x in range(n):
        for y in range(n):
            for z in range(n):
                mat = run(script, x, y, z, time=time)
                grid.append((x, y, z, mat))
    return grid


def draw_grid(grid, n=16):
    # Clear previous drawings
    dpg.delete_item("drawing_container", children_only=True)

    # Scale factor to position cubes
    scale = 1.0 / n

    for x, y, z, mat in grid:
        if mat == "air":
            continue  # Skip air blocks

        color = MATERIALS.get(mat, (1, 0, 0, 1))  # Default to red if material not found

        # Calculate position (centered around origin)
        pos_x = (x - n / 2) * scale * 2
        pos_y = (y - n / 2) * scale * 2
        pos_z = (z - n / 2) * scale * 2

        # Draw cube
        with dpg.draw_node(parent="drawing_container"):
            dpg.draw_cube(
                (pos_x, pos_y, pos_z),
                (pos_x + scale, pos_y + scale, pos_z + scale),
                color=color,
                fill=color,
            )


def save_callback():
    print("Save Clicked")


def main():
    dpg.create_context()

    # Enable 3D mode
    dpg.configure_app(docking=True, docking_space=True)
    dpg.configure_app(init_file="dpg.ini")

    with dpg.window(label="3D Grid Viewer", width=800, height=600):
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Update",
                callback=lambda: draw_grid(generate_grid(time=1.5)),
            )
            dpg.add_button(label="Save", callback=save_callback)

        with dpg.drawlist(width=800, height=600, tag="drawing_container"):
            pass  # Will be filled by draw_grid()

    # Set up the 3D viewport
    with dpg.handler_registry():
        dpg.add_mouse_drag_handler(
            callback=lambda s, a: dpg.set_viewport_small_icon("icon.ico")
        )

    dpg.create_viewport(title="3D Material Grid", width=800, height=600)
    dpg.setup_dearpygui()

    # Initial draw
    draw_grid(generate_grid())

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
