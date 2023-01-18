from Polygon import Polygon
from Interface import Interface
from FunctionTab import FunctionTab
from Line import Line
import math

# 17 methods
class Arc(Polygon): # Converting to Polygon

  #_angle_marker = pygame.image.load("./line_color.png")

  def __init__(self, X, Y, _gs):

    super().__init__(X, Y, _gs)

    #objects.append(self)
    self.radius = 20
    #self.anchor = None
    self.angle = 0
    self.curve = 45
    self.type = "Arc Object"
    #self.grid_size = 10
    #self.selected = False
    #self.line_segments = []
    #self.angle_marker = ._angle_marker.copy()
    #self.angle_selected = False
    #self.interface = None
    self.set_curve(45)

  def extended_interface(self, interface):
    interface.set_text(self.type)
    new_interface = interface

    self.interface = new_interface

    angle_interface = Interface("Angle", new_interface, None)
    curve_interface = Interface("Curve", new_interface, None)

    angle_interface.function_tabs = [
      FunctionTab(self.set_angle_0, "set 0"),
      FunctionTab(self.decrement_angle, FunctionTab._down_arrow),
      FunctionTab(self.get_angle, "", "display"),
      FunctionTab(self.increment_angle, FunctionTab._up_arrow)
    ]

    curve_interface.function_tabs = [
      FunctionTab(self.set_curve_0, "set 0"),
      FunctionTab(self.decrement_curve, FunctionTab._down_arrow),
      FunctionTab(self.get_curve, "", "display"),
      FunctionTab(self.increment_curve, FunctionTab._up_arrow)
    ]

  #def build_arc(self):
  #  if self.anchor == None or self.radius == None or self.curve == None:
  #    return

  #  for c in range(self.curve // 4):


  def set_grid_size(self, grid_size):
    for l in self.vertices:
      l.set_grid_size(grid_size)

  def increment_radius(self):
    self.set_radius(self.radius + 10)

  def decrement_radius(self):
    self.set_radius(max(self.radius - 10, 0))

  def set_radius_0(self):
    self.set_radius(0)

  def get_radius(self):
    return self.radius

  def increment_angle(self):
    self.set_angle(self.angle + 10)
  
  def decrement_angle(self):
    self.set_angle(self.angle - 10)

  def set_angle_0(self):
    self.set_angle(0)

  def get_angle(self):
    return self.angle

  def increment_curve(self):
    self.set_curve(self.curve + 10)

  def decrement_curve(self):
    self.set_curve(max(self.curve - 10, 0))

  def set_curve_0(self):
    self.set_curve(0)

  def get_curve(self):
    return self.curve

  def set_radius(self, radius, step=5):
    self.radius = radius

    if self.anchor == None:
      return

    self.vertices = []

    _n = step
    for c in range(self.curve // _n):
      pc_a_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)
      pc_a_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)

      n = Line(queue=False)
      n.set_anchor(pc_a_x, pc_a_y)
      n.set_end(pc_b_x, pc_b_y)
      n.grid_size = self.grid_size

      self.vertices.append(n)

  def set_curve(self, curve, step=5):
    self.curve = curve

    if self.anchor == None:
      return

    self.vertices = []

    _n = step
    for c in range(self.curve // _n):
      pc_a_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)
      pc_a_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)

      n = Line(queue=False)
      n.set_anchor(pc_a_x, pc_a_y)
      n.set_end(pc_b_x, pc_b_y)
      n.grid_size = self.grid_size

      self.vertices.append(n)