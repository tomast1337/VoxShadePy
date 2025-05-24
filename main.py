from dearpygui import dearpygui as dpg
from interpreter import run


script = """
r = x * 0.5 + sin(time) * 3;
if y < r {
  return crystal;
}
return air;
"""

for y in range(16):
    result = run(script, x=4, y=y, z=4, time=1.5)
    print(f"y={y}: {result}")
