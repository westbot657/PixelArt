# Pixelator
# vector and bitmap art
# Weston Day 2021

import os
import math
import pygame
import json
import re

#import time

from threading import Thread
from PIL import Image, ImageColor

Screen = pygame.display.set_mode((625, 250), pygame.RESIZABLE)

######################################
## ------ Generate Resources ------ ##
######################################
from Resources import *

mode = "selection"
modes = [
  "selection",
  "vertex edit",
  "vector erase",
  "bitmap draw",
  "bitmap erase",
  # "bitmap fill"
]

pygame.font.init()
#objects = []
#################################################
## ------ Initialize custom object list ------ ##
## ------     and other variables       ------ ##
#################################################
from Objects import Objects
objects = Objects()
events = []
ui = []
last_mouse_press = [False, False, False]
mouse_press = None
mouse_pos = None

_ui_color = (80, 80, 80, 255)

from TextInput import TextInput
TextInput.init(pygame)

from ColorSelector import ColorSelector
ColorSelector.init(pygame)

from FunctionTab import FunctionTab
FunctionTab.init(pygame)

from Interface import Interface
Interface.init(pygame)

_gs = 8
def gs_down():
  global _gs
  _gs -= 1
  for obj in objects:
    obj.set_grid_size(_gs)

def gs_disp():
  global _gs
  return _gs

def gs_up():
  global _gs
  _gs += 1
  for obj in objects:
    obj.set_grid_size(_gs)

def clear():
  global objects
  for obj in objects:
    obj.delete()

  objects.set([])

from Place import Place
ui.append(Place)

from Grab import Grab

###############################################
## ------ Initialize Geometry Classes ------ ##
###############################################

from Line import Line
Line.init(pygame, Interface, FunctionTab, Grab, objects)

from Polygon import Polygon, post_init
Polygon.init(pygame, Interface, FunctionTab, TextInput, ColorSelector, objects)

from Triangle  import Triangle
from Rectangle import Rectangle
from Arc       import Arc
from Circle    import Circle

#############################
## ------ Post Init ------ ##
#############################
post_init(Line, Triangle, Rectangle, Arc, Circle)

class Animation:
  _objects = []

  def __init__(self, poly=None, commands=[], loop=True):
    self.commands = commands
    self.poly = poly
    self.iter = enumerate(commands)
    self.loop = loop
    self.running = False
    Animation._objects.append(self)

  def start(self):
    self.running = True

  def stop(self):
    self.running = False

  def step(self):
    try:
      i, run = next(self.iter)
    except StopIteration:
      self.iter = enumerate(self.commands)
      i, run = next(self.iter)
    
    exec(f"self.poly.{run['command']}(**{run['kwargs']})")

  def check_select(self, *args, **kwargs):
    pass

  def _update(self, *args, **kwargs):

    if (not self.running) or (len(self.commands) == 0) or (self.poly == None):
      return

    self.step()

  @classmethod
  def update(cls, *args, **kwargs):
    for obj in cls._objects:
      obj._update()


class mouse_grid:
  
  @staticmethod
  def check_select(*a, **b):
    pass

  @staticmethod
  def update(screen):

    if not show_environment_grid:
      return

    w = screen.get_width()
    h = screen.get_height()

    W = (w//_gs) + 1
    H = (h//_gs) + 1

    for y in range(H):
      screen.fill(
        (100, 100, 100, 127),
        (0, y*_gs, w*_gs, 1)
      )

    for x in range(W):
      screen.fill(
        (100, 100, 100, 127),
        (x*_gs, 0, 1, h*_gs)
      )

ui.append(mouse_grid)

rotate_anim = Animation(
  commands = [{"command": "rotate", "kwargs": {"angle": 5}}]
)

def animate(poly: Polygon, anim:str="rotate"):
  if anim == "rotate":
    return Animation(
      poly = poly,
      commands = [
        {
          "command": "rotate",
          "kwargs": {
            "angle": 5
          }
        }
      ]
    )
  
  elif anim == "scale":
    c = {
      "command": "increment_scale",
      "kwargs": {}
    }
    c1 = {
      "command": "decrement_scale",
      "kwargs": {}
    }
    return Animation(
      poly = poly,
      commands = [
        c, c, c, c, c, c, c, c, c, c, c, c, c, c, c,
        c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1,
        c1, c1, c1, c1, c1, c1, c1, c1, c1,
        c, c, c, c, c, c, c, c, c, c
      ]
    )

ui.append(Animation)

def set_mode(m):
  global mode
  mode = m

show_line = True
show_grid = False
show_environment_grid = True
show_object_fill = False
running = True
def InputLoop():
  global running, show_line, mode, objects, rotate_anim
  while running:
    user_in = input("enter cmd > ")
    if user_in == "":
      continue
    try:
      exec(
        f"""n = {user_in}\nif n != None:\n  print(n)"""
        )
    except Exception as e:
      print(e)

def to_image(objs, name):
  raw_data = []
  for obj in objs:
    if isinstance(obj, Line):
      if len(obj.draws) == 0:
        obj._threaded_trace()
        # raise ValueError("object fill hasn't been activated")
      for d in obj.draws:
        raw_data.append((d, obj.grid_color))
    
    else:
      for v in obj.vertices:
        if len(v.draws) == 0:
          v._threaded_trace()
          # raise ValueError("object fill hasn't been activated")
        for d in v.draws:
          raw_data.append((d, obj.grid_color))

  min_x = 1000
  min_y = 1000
  max_x = 0
  max_y = 0
  for t in raw_data:
    pos, col = t
    x, y, w, h = pos

    x = x//_gs
    y = y//_gs
    
    min_x = min(x, min_x)
    min_y = min(y, min_y)
    max_x = max(x, max_x)
    max_y = max(y, max_y)

  width = int(max_x - min_x) + 1
  height = int(max_y - min_y) + 1

  data = [[(0, 0, 0, 0) for j in range(width)] for i in range(height)]

  for t in raw_data:
    pos, col = t
    x, y, w, h = pos
    x = x//_gs
    y = y//_gs

    x -= min_x
    y -= min_y

    x = int(x)
    y = int(y)
    if len(col) == 3:
      r, g, b = col
      data[y][x] = (r, g, b, 255)

    elif len(col) == 4:
      r, g, b, a = col
      data[y][x] = (r, g, b, a)

  dat = []
  for l in data:
    for _l in l:
      dat.append(_l)

  img = Image.new("RGBA", (width, height))
  img.putdata(dat)
  img.save(f"{name}.png")


def get(i=0):
  return objects[i]

def hide_lines():
  global show_line
  show_line = False

def show_lines():
  global show_line
  show_line = True

def show_grids():
  global show_grid
  show_grid = True

def hide_grids():
  global show_grid
  show_grid = False

def show_env_grids():
  global show_environment_grid
  show_environment_grid = True

def hide_env_grids():
  global show_environment_grid
  show_environment_grid = False

def show_geometry_fill():
  global show_object_fill
  show_object_fill = True

def hide_geometry_fill():
  global show_object_fill
  show_object_fill = False

_bg_color = (127, 127, 127)
def set_bg_color(color):
  global _bg_color, _ui_color
  _bg_color = color
  r, g, b, a = color
  _ui_color = (((255-r)/2)+127, ((255-g)/2)+127, ((255-b)/2)+127, ((255-a)/2)+127)

def get_bg_color():
  global _bg_color
  return _bg_color

def get_mode():
  return mode

main_interface = Interface("Environment")

mode_interface = Interface("Mode", main_interface, expanded=None)

mode_interface.function_tabs = [
  FunctionTab(get_mode, "", "display"),
  FunctionTab(set_mode, "[Selection]", kwargs={"m": "selection"}),
  FunctionTab(set_mode, "[Vertex Edit]", kwargs={"m": "vertex edit"})
]

gs = Interface("Grid Size", main_interface, expanded=None)
gsdown = FunctionTab(gs_down, FunctionTab._down_arrow)
gsdisp = FunctionTab(gs_disp, "", "display")
gsup = FunctionTab(gs_up, FunctionTab._up_arrow)

gs.function_tabs = [gsdown, gsdisp, gsup]

bgc = Interface("Background Color", main_interface, expanded=None)
bgset = FunctionTab(ColorSelector, "[Select]", kwargs={"x": 1000, "y": 1000, "return_to": set_bg_color, "initial_color": get_bg_color})
bgc.function_tabs = [bgset]

_fills = Interface("Fill Geometry", main_interface, expanded=None)
_fills.function_tabs = [
  FunctionTab(show_geometry_fill, FunctionTab._invisible, "toggle", func2=hide_geometry_fill, surface2=FunctionTab._visible)
]

_env_grids = Interface("Grid", main_interface, expanded=None)
_env_grids.function_tabs = [
  FunctionTab(hide_env_grids, FunctionTab._visible, "toggle", func2=show_env_grids, surface2=FunctionTab._invisible)
]
_grids = Interface("Fill", main_interface, expanded=None)
_grids.function_tabs = [
  FunctionTab(show_grids, FunctionTab._invisible, "toggle", func2=hide_grids, surface2=FunctionTab._visible)
]
_lines = Interface("Lines", main_interface, expanded=None)
_lines.function_tabs = [
  FunctionTab(hide_lines, FunctionTab._visible, "toggle", func2=show_lines, surface2=FunctionTab._invisible)
]


def place_polygon():
  Polygon(mouse_pos[0], mouse_pos[1], _gs)

def place_line():
  l = Line()
  l.set_anchor(mouse_pos[0], mouse_pos[1])

def place_rectangle():
  Rectangle(mouse_pos[0], mouse_pos[1], 100, 100, _gs)

def place_triangle():
  Triangle(mouse_pos[0], mouse_pos[1], 50, _gs)

def place_arc():
  Arc(mouse_pos[0], mouse_pos[1], _gs)

def place_circle():
  Circle(mouse_pos[0], mouse_pos[1], 100, _gs)

create_interface = Interface("Create", main_interface, expanded=None)

create_interface.function_tabs = [
  FunctionTab(Place, FunctionTab._polygon, kwargs={"obj": place_polygon}),
  FunctionTab(Place, FunctionTab._rectangle, kwargs={"obj": place_rectangle}),
  FunctionTab(Place, FunctionTab._triangle, kwargs={"obj": place_triangle}),
  FunctionTab(Place, FunctionTab._circle, kwargs={"obj": place_circle}),
  FunctionTab(Place, FunctionTab._arc, kwargs={"obj": place_arc}),
  FunctionTab(Place, FunctionTab._line, kwargs={"obj": place_line})
]

def load_pattern(identifier):

  p = os.scandir()
  names = [n.name for n in p]

  possible_configs = []
  for n in names:
    if n.endswith(".json"):
      possible_configs.append(n)

  results = []
  for n in possible_configs:
    if identifier in n:
      results.append(n)

  if len(results) == 1:
    Polygon.load_config(json.load(open(f"./{results[0]}")))
  
  elif len(results) == 0:
    raise Exception("No Pattern could be found")
  
  else:
    Polygon.load_configs([json.load(open(f"./{n}")) for n in results])
    #raise Exception(f"Multiple Patterns match identifier '{identifier}': {results}")

#poly = Rectangle(336, 142, 100, 100, 25)

def FillLoop():
  global show_object_fill, running
  while running:
    while show_object_fill:
      for obj in objects:
        obj._fill()

FillThread = Thread(target=FillLoop)

split_trace_threads = False
def TraceLoop():
  global split_trace_threads, show_grid
  while not split_trace_threads:
    while show_grid:
      for obj in objects:
        obj._single_thread_trace()

      if split_trace_threads:
        break

TraceThread = Thread(target=TraceLoop)

FillThread.start()
TraceThread.start()


def single_thread_tracers():
  global split_trace_threads

  if split_trace_threads:
    split_trace_threads = False
    # setting to false should causes TraceThread to stop

    for obj in objects:
      obj.TraceThread.start()

def multi_thread_tracers():
  global split_trace_threads

  if not split_trace_threads:
    split_trace_threads = True
    # setting to true should cause all polygon threads to stop
    TraceThread.start()

InputThread = Thread(target=InputLoop)
InputThread.start()

while running:
  Screen.fill(_bg_color)

  mouse_press = list(pygame.mouse.get_pressed())
  mouse_pos = pygame.mouse.get_pos()

  events = []
  for event in pygame.event.get():
    events.append(event)

  for obj in ui:
    obj.check_select(Screen, mouse_press, last_mouse_press)
    obj.update(Screen)

  if show_object_fill:
    for obj in objects:
      obj.fill(Screen, _gs)

  if show_grid:
    for obj in objects:
      obj.trace(Screen)

  if show_line:
    Grab.update(mouse_pos, mouse_press, last_mouse_press)
    for obj in objects:
      obj.update(Screen, mouse_pos, mouse_press, last_mouse_press, mode)


  for obj in objects:
    obj.check_select(Screen, mouse_press, last_mouse_press, mouse_pos)

  Interface.update(Screen, events, _ui_color, mouse_pos, mouse_press, last_mouse_press)

  ColorSelector.check_select(Screen, mouse_press, last_mouse_press, mouse_pos)
  ColorSelector.update(Screen, _ui_color, mouse_pos)

  TextInput.check_select(Screen)
  TextInput.update(Screen, events)

  if mouse_press != last_mouse_press:
    last_mouse_press = mouse_press

  pygame.display.update()
