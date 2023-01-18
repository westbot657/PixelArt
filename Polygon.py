from threading import Thread
import json
import math

Line = None
Triangle = None
Rectangle = None
Arc = None
Circle = None

def post_init(line, triangle, rectangle, arc, circle):
  global Line, Triangle, Rectangle, Arc, Circle
  Line = line
  Triangle = triangle
  Rectangle = rectangle
  Arc = arc
  Circle = circle

# 62 methods!?!?!
class Polygon:

  pygame = None
  Interface = None
  FunctionTab = None
  ColorSelector = None
  _angle_marker = None
  
  @classmethod
  def init(cls, pygame, Interface, FunctionTab, TextInput, ColorSelector, objects):
    cls.pygame = pygame
    cls.Interface = Interface
    cls.FunctionTab = FunctionTab
    cls.objects = objects
    cls.TextInput = TextInput
    cls.ColorSelector = ColorSelector

    cls._angle_marker = pygame.image.load("./resources/line_color.png")
  
  def __init__(self, X, Y, _gs):
    self.anchor = [X, Y]
    self.vertices = []
    self.grid_color = (0, 0, 0)

    self.transform_history = []

    self.history_seek = -1
    self.rotation = 0
    self.grid_size = _gs
    self.horizontal_scale = 1
    self.verticle_scale = 1
    self.scale = 1
    self.width_scale = 1
    self.height_scale = 1
    self.fills = []

    self.history_lock = False
    self.selected = False
    self.angle_selected = False
    self.anchor_selected = False
    self.scale_selected = False
    self.height_scale_selected = False
    self.width_scale_selected = False
    self.verticle_scale_selected = False
    self.horizontal_scale_selected = False

    self.type = "Polygon Object"

    self.interface = None

    self.colorview = self.FunctionTab._x.copy()
    #self.colorview.fill(self.grid_color)
    self.set_color(self.grid_color)

    self.angle_marker = Polygon._angle_marker.copy()
    self.TraceThread = Thread(target=self._threaded_trace)
    self.FillThread = Thread(target=self._fill)

    #self.TraceThread.start()

    self.objects.append(self)

    self.add_vertice_from_last(10, 180)

  def extend_config(self, config):
    return config

  @classmethod
  def update_config(cls, config, _gs):
    if "horizontal_scale" not in config.keys():
      config.update({"horizontal_scale": 1})
    
    if "verticle_scale" not in config.keys():
      config.update({"verticle_scale": 1})
    
    if "height_scale" not in config.keys():
      config.update({"height_scale": 1})

    if "width_scale" not in config.keys():
      config.update({"width_scale": 1})

    if "grid_color" not in config.keys():
      config.update({"grid_color": (0, 0, 0, 255)})

    if "grid_size" not in config.keys():
      config.update({"grid_size": _gs})


  def save_config(self, _gs):
    config = {
      "anchor": self.anchor.copy(),
      "scale": self.scale,
      "horizontal_scale": self.horizontal_scale,
      "verticle_scale": self.verticle_scale,
      "height_scale": self.height_scale,
      "width_scale": self.width_scale,
      "type": self.type,
      "kwargs": {"X": self.anchor[0], "Y": self.anchor[1]},
      "grid_size": self.grid_size,
      "grid_color": list(self.grid_color),
      "rotation": self.rotation,
      "vertices": [
        {
          "anchor": l.anchor.copy(),
          "angle": l.angle,
          "length": l.length,
          "width": l.width
        } for l in self.vertices
      ]
    }
    return self.extend_config(config, _gs)

  @classmethod
  def load_config(cls, config):
    #anchor = [float(config["anchor"][0]), float(config["anchor"][1])]
    scale = float(config["scale"])
    horizontal_scale = float(config["horizontal_scale"])
    verticle_scale = float(config["verticle_scale"])
    width_scale = float(config["width_scale"])
    height_scale = float(config["height_scale"])
    _type = str(config["type"])
    kwargs = config["kwargs"]
    grid_size = int(config["grid_size"])
    rotation = float(config["rotation"])
    vertice_configs = config["vertices"]
    grid_color = tuple(config["grid_color"])


    # This just became difficult...
    if _type == "Triangle Object":
      new_poly = Triangle(**kwargs)
    elif _type == "Arc Object":
      new_poly = Arc(**kwargs)
    elif _type == "Circle Object":
      new_poly = Circle(**kwargs)
    elif _type == "Rectangle Object":
      new_poly = Rectangle(**kwargs)
    elif _type == "Polygon Object":
      new_poly = Polygon(**kwargs)

    new_poly.set_scale(scale)
    new_poly.verticle_scale = verticle_scale
    new_poly.horizontal_scale = horizontal_scale
    new_poly.height_scale = height_scale
    new_poly.width_scale = width_scale
    new_poly.type = _type
    new_poly.set_grid_size(grid_size)
    new_poly.set_color(grid_color)
    new_poly.rotate_to(rotation)

    vertices = []
    for conf in vertice_configs:
      l = Line(queue=False)
      l.set_anchor(float(conf["anchor"][0]), int(conf["anchor"][1]))
      l.set_length(float(conf["length"]))
      l.set_angle(float(conf["angle"]))
      l.set_grid_size(grid_size)
      l.width = float(conf["width"])
      l.grid_color = grid_color
      vertices.append(l)

    new_poly.vertices = vertices

    return new_poly

  @classmethod
  def load_configs(cls, configs):
    for config in configs:
      cls.load_config(config)

  def name_save(self):
    self.TextInput(self.anchor[0] + 50, self.anchor[1] + 50, self.save)

  def save(self, filename):
    json.dump(self.save_config(), open(f"./{filename}.json", "w+"))

  def create_interface(self, parent=None):
    new_interface = self.Interface(self.type)
    self.interface = new_interface

    if parent == None:
      new_interface.function_tabs = [
        self.FunctionTab(self.name_save, self.FunctionTab._save),
        self.FunctionTab(self.remove_interface, self.FunctionTab._x),
        self.FunctionTab(self.delete, self.FunctionTab._trash)
      ]

    anchor_interface = self.Interface("Anchor", new_interface, None)
    rotate_interface = self.Interface("Rotate", new_interface, None)
    scale_interface = self.Interface("Scale", new_interface)
    color_interface = self.Interface("Color", new_interface, None)
    line_interface = self.Interface("Lines", new_interface, None)

    anchor_interface.function_tabs = [
      self.FunctionTab(self.calibrate_anchor, self.FunctionTab._align),
      self.FunctionTab(self.get_anchor, "", "display")
    ]

    rotate_interface.function_tabs = [
      self.FunctionTab(self.rotate_to, "set 0", kwargs={"angle": 0}),
      self.FunctionTab(self.rotate, self.FunctionTab._down_arrow, kwargs={"angle": -10}),
      self.FunctionTab(self.get_rotation, "", "display"),
      self.FunctionTab(self.rotate, self.FunctionTab._up_arrow, kwargs={"angle": 10})
    ]

    scale_interface.function_tabs = [
      self.FunctionTab(self.set_scale, "set 1", kwargs={"scale": 1}),
      self.FunctionTab(self.decrement_scale, self.FunctionTab._down_arrow),
      self.FunctionTab(self.get_scale, "", "display"),
      self.FunctionTab(self.increment_scale, self.FunctionTab._up_arrow)
    ]

    verticle_scale_interface = self.Interface("Verticle", scale_interface, None)
    horizontal_scale_interface = self.Interface("Horizontal",scale_interface, None)
    height_scale_interface = self.Interface("Height", scale_interface, None)
    width_scale_interface = self.Interface("Width", scale_interface, None)

    verticle_scale_interface.function_tabs = [
      self.FunctionTab(self.set_verticle_scale, "Set 1", kwargs={"verticle_scale": 1}),
      self.FunctionTab(self.decrement_verticle_scale, self.FunctionTab._down_arrow),
      self.FunctionTab(self.get_verticle_scale, "", "display"),
      self.FunctionTab(self.increment_verticle_scale, self.FunctionTab._up_arrow)
    ]

    horizontal_scale_interface.function_tabs = [
      self.FunctionTab(self.set_horizontal_scale, "Set 1", kwargs={"horizontal_scale": 1}),
      self.FunctionTab(self.decrement_horizontal_scale, self.FunctionTab._left_arrow),
      self.FunctionTab(self.get_horizontal_scale, "", "display"),
      self.FunctionTab(self.increment_horizontal_scale, self.FunctionTab._right_arrow)
    ]

    height_scale_interface.function_tabs = [
      self.FunctionTab(self.set_height_scale, "Set 1", kwargs={"height_scale": 1}),
      self.FunctionTab(self.decrement_height_scale, self.FunctionTab._down_arrow),
      self.FunctionTab(self.get_height_scale, "", "display"),
      self.FunctionTab(self.increment_height_scale, self.FunctionTab._up_arrow)
    ]

    width_scale_interface.function_tabs = [
      self.FunctionTab(self.set_width_scale, "Set 1", kwargs={"width_scale": 1}),
      self.FunctionTab(self.decrement_width_scale, self.FunctionTab._left_arrow),
      self.FunctionTab(self.get_width_scale, "", "display"),
      self.FunctionTab(self.increment_width_scale, self.FunctionTab._right_arrow)
    ]

    color_interface.function_tabs = [
      self.FunctionTab(self.ColorSelector, self.colorview, kwargs={"x": 1000, "y": 1000, "return_to": self.set_color, "initial_color": self.get_color})
    ]

    line_interface.function_tabs = [
      self.FunctionTab(self.add_vertice_from_last, self.FunctionTab._add_line_end, kwargs={"length": 20, "angle": 90}),
      self.FunctionTab(self.add_vertice_from_last, self.FunctionTab._add_line_start, kwargs={"length": 20, "angle": 90, "index": 0}),
      self.FunctionTab(self.remove_vertice, self.FunctionTab._remove_line_end),
      self.FunctionTab(self.remove_vertice, self.FunctionTab._remove_line_start, kwargs={"i": 0})
    ]

    self.extended_interface(new_interface)

  def extended_interface(self, interface):
    pass

  def delete(self):
    self.remove_interface()
    self.objects.remove(self)
    del self

  def get_color(self):
    return self.grid_color

  def remove_interface(self):
    self.Interface._children.remove(self.interface)
    self.interface = None  

  def snap(self):
    self.move_to(
      ((self.anchor[0]//self.grid_size)*self.grid_size),
      ((self.anchor[1]//self.grid_size)*self.grid_size)
    )

  def calibrate_anchor(self):

    self.add_to_history(
      {
        "Event": "self.calibrate_anchor()",
        "EventValue": None,
        "Inverse": "self.set_anchor(*{})",
        "InverseValue": tuple(self.anchor.copy()),
        "Flags": ["Add-Values"]
      }
    )
    sum_x = 0
    sum_y = 0
    l = len(self.vertices) * 2
    for v in self.vertices:
      sum_x += v.anchor[0] + v.end[0]
      sum_y += v.anchor[1] + v.end[1]

    self.anchor = [sum_x/l, sum_y/l]

  def set_scale(self, scale):

    self.add_to_history(
      {
        "Event": "self.set_scale({})",
        "EventValue": scale,
        "Inverse": "self.set_scale({})",
        "InverseValue": self.scale,
        "Flags": ["Replace-Event-Value"]
      }
    )
    
    scale = max(0.1, scale)

    for v in self.vertices:
      prev_anchor = v.anchor.copy()
      prev_end = v.end.copy()

      a_dx = prev_anchor[0] - self.anchor[0]
      a_dy = prev_anchor[1] - self.anchor[1]
      anchor_dist = math.sqrt(
        (a_dx ** 2) +
        (a_dy ** 2)
      )

      e_dx = prev_end[0] - self.anchor[0]
      e_dy = prev_end[1] - self.anchor[1]
      end_dist = math.sqrt(
        (e_dx ** 2) +
        (e_dy ** 2)
      )

      if anchor_dist != 0:
        a_s = math.degrees(math.asin(a_dy/anchor_dist))
        if a_s == 0:
          a_s = 1

        angle_to_anchor = math.degrees(math.acos(a_dx/anchor_dist)) * (a_s/abs(a_s))
      else:
        angle_to_anchor = 0
      
      if end_dist != 0:
        e_s = math.degrees(math.asin(e_dy/end_dist))
        if e_s == 0:
          e_s = 1

        angle_to_end = math.degrees(math.acos(e_dx/end_dist)) * (e_s/abs(e_s))
      else:
        angle_to_end = 0

      scale_dist_a = (anchor_dist / self.scale) * scale
      scale_dist_e = (end_dist / self.scale) * scale

      new_ax = math.cos(math.radians(angle_to_anchor)) * scale_dist_a
      new_ay = math.sin(math.radians(angle_to_anchor)) * scale_dist_a

      new_ex = math.cos(math.radians(angle_to_end)) * scale_dist_e
      new_ey = math.sin(math.radians(angle_to_end)) * scale_dist_e

      v.set_anchor(self.anchor[0] + new_ax, self.anchor[1] + new_ay)
      v.set_end(self.anchor[0] + new_ex, self.anchor[1] + new_ey)

      del new_ax, new_ay, new_ex, new_ey, scale_dist_a, scale_dist_e, angle_to_anchor, angle_to_end, anchor_dist, end_dist

    self.scale = scale

  def decrement_scale(self):
    self.set_scale(round(max(0.1, self.scale - 0.1), 1))

  def increment_scale(self):
    self.set_scale(round(self.scale + 0.1, 1))

  def get_scale(self):
    return self.scale

  def get_rotation(self):
    return self.rotation

  def get_anchor(self):
    return self.anchor

  def set_verticle_scale(self, verticle_scale):

    self.add_to_history(
      {
        "Event": "self.set_verticle_scale({})", 
        "EventValue": verticle_scale,
        "Inverse": "self.set_verticle_scale({})",
        "InverseValue": float(str(self.verticle_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    verticle_scale = max(verticle_scale, 0.1)
    rate = (verticle_scale / self.verticle_scale)
    for v in self.vertices:
      dy = v.anchor[1] - self.anchor[1]
      dy1 = v.end[1] - self.anchor[1]
      dy *= rate
      dy1 *= rate
      v.set_anchor(v.anchor[0], self.anchor[1] + dy)
      v.set_end(v.end[0], self.anchor[1] + dy1)
    self.verticle_scale = verticle_scale

  def set_horizontal_scale(self, horizontal_scale):

    self.add_to_history(
      {
        "Event": "self.set_horizontal_scale({})",
        "EventValue": horizontal_scale,
        "Inverse": "self.set_horizontal_scale({})",
        "InverseValue": float(str(self.horizontal_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    horizontal_scale = max(horizontal_scale, 0.1)
    rate = (horizontal_scale/self.horizontal_scale)
    for v in self.vertices:
      dx = v.anchor[0] - self.anchor[0]
      dx1 = v.end[0] - self.anchor[0]
      dx *= rate
      dx1 *= rate
      v.set_anchor(self.anchor[0] + dx, v.anchor[1])
      v.set_end(self.anchor[0] + dx1, v.end[1])
    self.horizontal_scale = horizontal_scale

  def increment_horizontal_scale(self):
    self.set_horizontal_scale(round(self.horizontal_scale + 0.1, 1))

  def decrement_horizontal_scale(self):
    self.set_horizontal_scale(round(max(self.horizontal_scale - 0.1, 0.1), 1))

  def increment_verticle_scale(self):
    self.set_verticle_scale(round(self.verticle_scale + 0.1, 1))
  
  def decrement_verticle_scale(self):
    self.set_verticle_scale(round(max(self.verticle_scale - 0.1, 0.1), 1))

  def get_verticle_scale(self):
    return self.verticle_scale
  
  def get_horizontal_scale(self):
    return self.horizontal_scale

  def get_height_scale(self):
    return self.height_scale
  
  def get_width_scale(self):
    return self.width_scale

  def set_height_scale(self, height_scale):

    self.add_to_history(
      {
        "Event": "self.set_height_scale({})",
        "EventValue": height_scale,
        "Inverse": "self.set_height_scale({})",
        "InverseValue": float(str(self.height_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    self.history_lock = True
    height_scale = max(height_scale, 0.1)
    r = self.rotation
    rate = (height_scale / self.height_scale)
    self.rotate_to(0)
    for v in self.vertices:
      dy = v.anchor[1] - self.anchor[1]
      dy1 = v.end[1] - self.anchor[1]
      dy *= rate
      dy1 *= rate
      v.set_anchor(v.anchor[0], self.anchor[1] + dy)
      v.set_end(v.end[0], self.anchor[1] + dy1)
    self.height_scale = height_scale
    self.rotate_to(r)
    self.history_lock=False

  def set_width_scale(self, width_scale):

    self.add_to_history(
      {
        "Event": "self.set_width_scale({})",
        "EventValue": width_scale,
        "Inverse": "self.set_width_scale({})",
        "InverseValue": float(str(self.width_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    self.history_lock = True
    width_scale = max(width_scale, 0.1)
    r = self.rotation
    rate = (width_scale/self.width_scale)
    self.rotate_to(0)
    for v in self.vertices:
      dx = v.anchor[0] - self.anchor[0]
      dx1 = v.end[0] - self.anchor[0]
      dx *= rate
      dx1 *= rate
      v.set_anchor(self.anchor[0] + dx, v.anchor[1])
      v.set_end(self.anchor[0] + dx1, v.end[1])
    self.width_scale = width_scale
    self.rotate_to(r)
    self.history_lock = False

  def increment_height_scale(self):
    self.set_height(self.height_scale + 0.1)

  def decrement_height_scale(self):
    self.set_height(max(0.1, self.height - 0.1))

  def increment_width_scale(self):
    self.set_width_scale(self.length + 0.1)

  def decrement_width_scale(self):
    self.set_width_scale(max(0.1, self.length - 0.1))

  def check_select(self, screen, mouse_press, last_mouse_press, mouse_pos):
    minpos = None
    maxpos = None

    if mouse_press[0] == False and last_mouse_press[0] == True:
      self.add_to_history(
        {
          "Event": "# Skip",
          "EventValue": None,
          "Inverse": "# Skip",
          "InverseValue": None,
          "Flags": ["AddValues"]
        }
      )

    if len(self.vertices) == 0:
      return

    for l in self.vertices:
      if minpos == None:
        minpos = [min(l.anchor[0], l.end[0]), min(l.anchor[1], l.end[1])]

      if maxpos == None:
        maxpos = [max(l.anchor[0], l.end[0]), max(l.anchor[1], l.end[1])]
      
      minpos[0] = min(
        min(l.anchor[0], l.end[0]),
        minpos[0]
      )
      minpos[1] = min(
        min(l.anchor[1], l.end[1]),
        minpos[1]
      )
      maxpos[0] = max(
        max(l.anchor[0], l.end[0]),
        maxpos[0]
      )
      maxpos[1] = max(
        max(l.anchor[1], l.end[1]),
        maxpos[1]
      )

    if mouse_press[0] == True and last_mouse_press[0] == False:
      if minpos[0] - 1 <= mouse_pos[0] and maxpos[0] + 1 >= mouse_pos[0] and minpos[1] - 1 <= mouse_pos[1] and maxpos[1] + 1 >= mouse_pos[1]:
        self.selected = True

        if self.interface == None:
          self.create_interface()

      elif self.selected == True:
        self.selected = False

    if self.selected:
      screen.fill(
        (0, 255, 0),
        (minpos[0], minpos[1], maxpos[0] - minpos[0], 1)
      )
      screen.fill(
        (0, 255, 0),
        (minpos[0], minpos[1], 1, maxpos[1] - minpos[1])
      )
      screen.fill(
        (0, 255, 0),
        (maxpos[0], minpos[1], 1, maxpos[1] - minpos[1])
        )
      screen.fill(
        (0, 255, 0),
        (minpos[0], maxpos[1], maxpos[0] - minpos[0], 1)
      )

  def rotate(self, angle):

    self.add_to_history(
      {
        "Event": "self.rotate({})",
        "EventValue": angle,
        "Inverse": "self.rotate({})",
        "InverseValue": -angle,
        "Flags": ["AddValues"]
      }
    )
    anchor = self.anchor.copy()

    self.rotation += angle

    for v in self.vertices:

      dx = v.anchor[0] - anchor[0]
      dy = v.anchor[1] - anchor[1]

      dist = math.sqrt((dx ** 2) + (dy ** 2))

      if dist != 0:
        s = math.degrees(math.asin(dy/dist))
        if s == 0:
          s = 1
        rot = math.degrees(math.acos(dx/dist)) * (s/abs(s))

        rot += angle

        new_x = math.cos(math.radians(rot)) * dist
        new_y = math.sin(math.radians(rot)) * dist

        v.set_anchor(anchor[0] + new_x, anchor[1] + new_y)

      v.set_angle(v.angle + angle)

  def rotate_to(self, angle):
    r = angle - self.rotation
    self.rotate(r)

  def rotate_towards(self, position):
    x, y = position

    dx = x - self.anchor[0]
    dy = y - self.anchor[1]

    dist = math.sqrt((dx ** 2) + (dy ** 2))

    if dist != 0:
      s = math.degrees(math.asin(dy/dist))
      if s == 0:
        s = 1
      rot = math.degrees(math.acos(dx/dist)) * (s/abs(s))

    else:
      rot = 0
    
    self.rotate_to(rot)

  def move(self, x, y):

    self.add_to_history(
      {
        "Event": "self.move(*{})",
        "EventValue": (x, y),
        "Inverse": "self.move(*{})",
        "InverseValue": (-x, -y),
        "Flags": ["AddValues"]
      }
    )
    self.anchor[0] += x
    self.anchor[1] += y

    for v in self.vertices:
      v.set_anchor(v.anchor[0] + x, v.anchor[1] + y)

  def move_to(self, x, y):
    dx = x - self.anchor[0]
    dy = y - self.anchor[1]

    self.move(dx, dy)

  def set_color(self, color):
    self.grid_color = color
    for v in self.vertices:
      v.set_color(color)

    self.colorview.fill(self.grid_color)

  def set_vertices(self, *vertices):

    #self.transform_history.append()
    self.vertices = list(vertices)
    for v in self.vertices:
      v.grid_color = self.grid_color

  def set_anchor(self, X, Y):
    self.add_to_history(
      {
        "Event": "self.set_anchor(*{})",
        "EventValue": (X, Y),
        "Inverse": "self.set_anchor(*{})",
        "InverseValue": tuple(self.anchor),
        "Flags": []
      }
    )
    self.anchor = [X, Y]

  def add_vertice(self, X, Y, index=-1):
    n = Line(queue=False)

    if len(self.vertices) == 0:
      if index < 0:
        n.set_anchor(*tuple(self.anchor))
      else:
        n.set_end(*tuple(self.anchor))

    else:
      if index < 0:
        n.set_anchor(*tuple(self.vertices[len(self.vertices) - 1].end))
      else:
        n.set_end(*tuple(self.vertices[index].end))

    if index < 0:
      n.set_end(X, Y)
    else:
      e = tuple(n.end)
      n.set_anchor(X, Y)
      n.set_end(*e)

    n.set_grid_size(self.grid_size)
    n.grid_color = self.grid_color

    if index < 0:
      self.vertices.append(n)
    
    else:
      self.vertices.insert(index, n)

  def remove_vertice(self, i=-1):
    try:
      self.vertices.remove(self.vertices[i])
    
    except:
      raise Exception(f"No Vertice Found in position {i}")

  def add_vertice_from_last(self, length, angle, relative_angle=True, index=-1):
    n = Line(queue=False)

    if len(self.vertices) == 0:
      n.set_anchor(*tuple(self.anchor))
      n.set_angle(angle)
      n.set_length(length)

    else:

      if index < 0:
        n.set_anchor(*tuple(self.vertices[len(self.vertices) - 1].end))

      else:
        n.set_anchor(*tuple(self.vertices[index].anchor))

      n.set_length(length)

      if relative_angle:
        n.set_angle(
          angle + self.vertices[len(self.vertices) - 1].angle
        )

        if index >= 0:
          n.set_angle(
            angle + self.vertices[index].angle
          )
          e = tuple(n.end)
          a = tuple(n.anchor)
          n.set_anchor(*e)
          n.set_end(*a)

      else:
        n.set_angle(angle)

    n.set_grid_size(self.grid_size)
    n.grid_color = self.grid_color

    if index < 0:
      self.vertices.append(n)

    else:
      self.vertices.insert(index, n)

  def set_grid_size(self, grid_size):
    self.add_to_history(
      {
        "Event": "self.set_grid_size({})",
        "EventValue": grid_size,
        "Inverse": "self.set_grid_size({})",
        "InverseValue": self.grid_size,
        "Flags": ["AddValues"]
      }
    )
    self.grid_size = grid_size
    for v in self.vertices:
      v.set_grid_size(grid_size)

  def add_to_history(self, event_obj):
    if self.history_lock:
      return
    
    if self.history_seek != -1:
      try:
        if self.history_seek < -1:
          x = len(self.transform_history)
          while True:
            self.transform_history.pop(x + self.history_seek)

        else:
          while True:
            self.transform_history.pop(self.history_seek)

      except:
        self.transform_history.append(
          {
            "Event": "# Skip",
            "EventValue": None,
            "Inverse": "# Skip",
            "InverseValue": None,
            "Flags": ["Replace-Event-Value"]
          }
        )

      self.history_seek = -1

    self.history_seek = -1
    if len(self.transform_history) == 0:
      self.transform_history.append(event_obj)

    elif "Replace-Event-Value" in event_obj["Flags"]:
      old = self.transform_history.pop(-1)
      if "Replace-Event-Value" in old["Flags"]:
        if event_obj["Event"] == old["Event"]:
          old["EventValue"] = event_obj["EventValue"]
          self.transform_history.append(old)

        else:
          self.transform_history.append(old)
          self.transform_history.append(event_obj)

      else:
        self.transform_history.append(old)
        self.transform_history.append(event_obj)

    elif "AddValues" in event_obj["Flags"]:
      old = self.transform_history.pop(-1)

      if "AddValues" in old["Flags"]:
        if event_obj["Event"] == old["Event"]:
          old_event_val = old["EventValue"]
          if isinstance(old_event_val, tuple):
            new_val1 = []
            new_val2 = []
            for x in range(len(old_event_val)):
              new_val1.append(old["EventValue"][x] + event_obj["EventValue"][x])
              new_val2.append(old["InverseValue"][x] + event_obj["InverseValue"][x])
            old["EventValue"] = tuple(new_val1)
            old["InverseValue"] = tuple(new_val2)

          elif isinstance(old_event_val, int) or isinstance(old_event_val, float):
            old["EventValue"] += event_obj["EventValue"]
            old["InverseValue"] += event_obj["InverseValue"]

          self.transform_history.append(old)
        
        else:
          self.transform_history.append(old)
          self.transform_history.append(event_obj)


      else:
        self.transform_history.append(old)
        self.transform_history.append(event_obj)

  def history(self):
    return self.transform_history

  def undo(self):
    self.history_lock = True
    if len(self.transform_history) == 0:
      self.history_lock = False
      print("Nothing left to undo")
      return

    event_obj = self.transform_history[self.history_seek]
    while event_obj["Event"] == "# Skip":
      self.transform_history.pop(len(self.transform_history) + self.history_seek)
      event_obj = self.transform_history[self.history_seek]
      if len(self.transform_history) + self.history_seek < 0:
        break

    invert = event_obj["Inverse"]
    #try:
    exec(f"{invert.format(str(event_obj['InverseValue']))}")
    
    #except Exception as e:
    #  print(f"Could not undo:\n{e}")
    #  self.history_lock = False
    #  return

    self.history_seek -= 1
    self.history_lock = False

  def redo(self):
    self.history_lock = True
    if len(self.transform_history) == 0 or self.history_seek == -1 or self.history_seek == len(self.transform_history) - 1:
      self.history_lock = False
      print("Nothing left to redo")
      return

    event_obj = self.transform_history[self.history_seek + 1]

    event = event_obj["Event"]

    try:
      exec(f"{event.format(str(event_obj['EventValue']))}")

    except:
      print("Could not redo")
      self.history_lock = False
      return

    self.history_seek += 1
    self.history_lock = False

  def _single_thread_trace(self):
    unique_draws = []
    for v in self.vertices:
      v._threaded_trace()

      replacement = []
      for draw in v.draws:
        if draw not in unique_draws:
          replacement.append(draw)
        
          unique_draws.append(draw)
      
      v.draws = replacement.copy()

  def _threaded_trace(self):
    global split_trace_threads
    while split_trace_threads:
      unique_draws = []
      for v in self.vertices:
        v._threaded_trace()

        replacement = []
        for draw in v.draws:
          if draw not in unique_draws:
            replacement.append(draw)
          
            unique_draws.append(draw)

  def trace(self, screen):
    for v in self.vertices:
      v.trace(screen)

  def _fill(self):

    # note: calculations will take a while

    # step 1: calculate all line segment rays
    # step 2: find the outermost edges of shape
    # step 3: raytrace from every outer edge inwards,
    # toggling whether to fill every time ray crosses a line
    # (watch out for if ray happens to run along a line)
    #   ^ would switch between fill/not fill

    pass

  def fill(self, screen, _gs):
    obj = self.pygame.transform.scale(Line._grid_object.copy(), (_gs, _gs))
    obj.fill(self.grid_color)
    obj.set_alpha(255)
    for pos in self.fills:
      x, y = pos
      
      screen.blit(
        obj, (x, y)
      )

  def extend_update(self, screen):
    pass

  def update(self, screen, mouse_pos, mouse_press, last_mouse_press, mode):

    if self.anchor == None:
      return

    for v in self.vertices:

      # TODO: replace mode with custom class
      v.update(screen, mouse_pos, mouse_press, last_mouse_press, mode)

    # angle
    xp = 30 * math.cos(math.radians(self.rotation))
    yp = 30 * math.sin(math.radians(self.rotation))

    xp += self.anchor[0]
    yp += self.anchor[1]

    screen.fill(
      (255, 255, 0),
      (xp - 1, yp - 1, 3, 3)
    )

    screen.fill(
      (255, 127, 0),
      (self.anchor[0] + ((math.cos(math.radians(45))*self.scale * 10) - 1), (self.anchor[1] - (math.sin(math.radians(45))*self.scale*10)) - 1, 3, 3)
    )

    screen.fill(
      (0, 127, 255),
      (
        (self.anchor[0] + (self.horizontal_scale * 10)) - 1,
        self.anchor[1] - 1, 3, 3
      )
    )

    screen.fill(
      (0, 127, 255),
      (
        self.anchor[0] - 1,
        (self.anchor[1] - (self.verticle_scale * 10)) - 1,
        3, 3
      )
    )

    screen.fill(
      (0, 200, 200),
      (
        (math.cos(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[0] - 1,
        (math.sin(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[1] - 1,
        3, 3
      )
    )

    screen.fill(
      (0, 200, 200),
      (
        (math.cos(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[0] - 1,
        (math.sin(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[1] - 1,
        3, 3
      )
    )

    # Line Manipulators
    if self.selected and mode == "vertex edit":
      screen.blit(
        self.FunctionTab._add_line_start,
        (
          self.anchor[0] - 45,
          self.anchor[1] - 45
        )
      )
      screen.blit(
        self.FunctionTab._add_line_end,
        (
          self.anchor[0] - 25,
          self.anchor[1] - 45
        )
      )
      screen.blit(
        self.FunctionTab._remove_line_start,
        (
          self.anchor[0] - 45,
          self.anchor[1] - 25
        )
      )
      screen.blit(
        self.FunctionTab._remove_line_end,
        (
          self.anchor[0] - 25,
          self.anchor[1] - 25
        )
      )

    if self.angle_selected:
      self.rotate_towards(mouse_pos)

    if self.anchor_selected:
      self.move_to(mouse_pos[0], mouse_pos[1])

    if self.scale_selected:
      self.set_scale(((mouse_pos[0] - self.anchor[0]) * math.sqrt(2)) / 10)

    if self.horizontal_scale_selected:
      self.set_horizontal_scale((mouse_pos[0] - self.anchor[0])/10)

    if self.verticle_scale_selected:
      self.set_verticle_scale((self.anchor[1] - mouse_pos[1])/10)

    if self.width_scale_selected:
      d = math.sqrt(((mouse_pos[1] - self.anchor[1]) ** 2) + ((mouse_pos[0] - self.anchor[0]) ** 2))
      
      self.set_width_scale(d / 10)

    if self.height_scale_selected:
      d = math.sqrt(((mouse_pos[1] - self.anchor[1]) ** 2) + ((mouse_pos[0] - self.anchor[0]) ** 2))
      
      self.set_height_scale(d / 10)

    if mouse_press[0] == True and last_mouse_press[0] == False and mode == "vertex edit":
      if xp - 2 <= mouse_pos[0] and xp + 2 >= mouse_pos[0] and yp - 2 <= mouse_pos[1] and yp + 2 >= mouse_pos[1]:
        self.angle_selected = True

      elif self.angle_selected:
        self.angle_selected = False

      if self.anchor[0] - 2 <= mouse_pos[0] and self.anchor[0] + 2 >= mouse_pos[0] and self.anchor[1] - 2 <= mouse_pos[1] and self.anchor[1] + 2 >= mouse_pos[1]:
        self.anchor_selected = True

      elif self.anchor_selected:
        self.anchor_selected = False

      # check scale selection
      if (self.anchor[0] + (math.cos(math.radians(45)) * self.scale * 10)) - 2 <= mouse_pos[0] and (self.anchor[0] + (math.cos(math.radians(45)) * self.scale * 10)) + 2 >= mouse_pos[0] and (self.anchor[1] - (math.sin(math.radians(45)) * self.scale * 10)) - 2 <= mouse_pos[1] and (self.anchor[1] - (math.sin(math.radians(45)) * self.scale * 10)) + 2 >= mouse_pos[1]:
        self.scale_selected = True
        self.anchor_selected = False

      elif self.scale_selected:
        self.scale_selected = False

      # check horizontal scale selection
      if (self.anchor[0] + (10 * self.horizontal_scale)) - 2 <= mouse_pos[0] and (self.anchor[0] + (10 * self.horizontal_scale)) + 2 >= mouse_pos[0] and self.anchor[1] - 2 <= mouse_pos[1] and self.anchor[1] + 2 >= mouse_pos[1]:
        self.horizontal_scale_selected = True
        self.anchor_selected = False

      elif self.horizontal_scale_selected:
        self.horizontal_scale_selected = False

      # check verticle scale selection
      if self.anchor[0] - 2 <= mouse_pos[0] and self.anchor[0] + 2 >= mouse_pos[0] and (self.anchor[1] - (10 * self.verticle_scale)) - 2 <= mouse_pos[1] and (self.anchor[1] - (10 * self.verticle_scale)) + 2 >= mouse_pos[1]:
        self.verticle_scale_selected = True
        self.anchor_selected = False

      elif self.verticle_scale_selected:
        self.verticle_scale_selected = False

      # check width scale selection
      if (math.cos(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[0] - 2 <= mouse_pos[0] and (math.cos(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[0] + 2 >= mouse_pos[0] and (math.sin(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[1] - 2 <= mouse_pos[1] and (math.sin(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[1] + 2 >= mouse_pos[1]:
        self.width_scale_selected = True
        self.anchor_selected = False

      elif self.width_scale_selected:
        self.width_scale_selected = False


      # check height scale selection
      if (math.cos(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[0] - 2 <= mouse_pos[0] and (math.cos(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[0] + 2 >= mouse_pos[0] and (math.sin(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[1] - 2 <= mouse_pos[1] and (math.sin(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[1] + 2 >= mouse_pos[1]:
        self.height_scale_selected = True
        self.anchor_selected = False

      elif self.height_scale_selected:
        self.height_scale_selected = False

      if self.selected:
        if self.anchor[0] - 46 <= mouse_pos[0] and self.anchor[0] - 29 >= mouse_pos[0] and self.anchor[1] - 46 <= mouse_pos[1] and self.anchor[1] - 29 >= mouse_pos[1]:
          self.add_vertice_from_last(20, 90, index=0)

        if self.anchor[0] - 26 <= mouse_pos[0] and self.anchor[0] - 9 >= mouse_pos[0] and self.anchor[1] - 46 <= mouse_pos[1] and self.anchor[1] - 29 >= mouse_pos[1]:
          self.add_vertice_from_last(20, 90)

        if self.anchor[0] - 46 <= mouse_pos[0] and self.anchor[0] - 29 >= mouse_pos[0] and self.anchor[1] - 26 <= mouse_pos[1] and self.anchor[1] - 9 >= mouse_pos[1]:
          self.remove_vertice(0)

        if self.anchor[0] - 26 <= mouse_pos[0] and self.anchor[0] - 9 >= mouse_pos[0] and self.anchor[1] - 26 <= mouse_pos[1] and self.anchor[1] - 9 >= mouse_pos[1]:
          self.remove_vertice()

    if mouse_press[0] == False and last_mouse_press[0] == True:
      self.angle_selected = False
      self.anchor_selected = False
      self.scale_selected = False
      self.width_scale_selected = False
      self.height_scale_selected = False
      self.verticle_scale_selected = False
      self.horizontal_scale_selected = False

    # anchor
    screen.fill(
      (255, 0, 255),
      (self.anchor[0] - 1, self.anchor[1] - 1, 3, 3)
    )

    self.extend_update(screen)