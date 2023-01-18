import math

class Line:

  _base = None
  _angle_marker = None
  _grid_object = None
  pygame = None
  Interface = None
  FunctionTab = None

  @classmethod
  def init(cls, pygame, Interface, FunctionTab, Grab, objects):
    cls._base = pygame.image.load("./resources/line_color.png")
    cls._angle_marker = cls._base.copy().fill((255, 255, 0))
    cls._grid_object = cls._base.copy()

    cls.pygame = pygame
    cls.Interface = Interface
    cls.FunctionTab = FunctionTab
    cls.objects = objects
    cls.Grab = Grab
  
  def __init__(self, *, queue=True):
    # TODO: create custom class for objects (which is a list)
    self.anchor = None
    self.end = None
    self.angle = 0
    self.length = 10
    self.width = 1
    self.grid_offset = (0, 0)
    self.grid_size = 20
    self.object = Line._base.copy()
    self.grid_color = (0, 0, 0)
    self.selected = False
    self.angle_marker = Line._angle_marker.copy()
    self.interface = None
    self.draws = []
    self.angle_selected = False
    if queue:
      self.objects.append(self)

  def create_interface(self, parent=None):
    new_selection = self.Interface("Line Object", parent=parent)
    self.interface = new_selection
    length_interface = self.Interface("Length", new_selection, None)
    angle_interface = self.Interface("Angle", new_selection, None)
    anchor_interface = self.Interface("Anchor", new_selection, None)
    end_interface = self.Interface("End", new_selection, None)

    if parent == None:
      new_selection.function_tabs = [
        self.FunctionTab(self.remove_interface, self.FunctionTab._x),
        self.FunctionTab(self.delete, self.FunctionTab._trash)
      ]

    length_interface.function_tabs = [
      self.FunctionTab(self.decrement_length, self.FunctionTab._down_arrow),
      self.FunctionTab(self.get_length, "", "display"),
      self.FunctionTab(self.increment_length, self.FunctionTab._up_arrow)
    ]

    angle_interface.function_tabs = [
      self.FunctionTab(self.set_angle_0, "set 0"),
      self.FunctionTab(self.decrement_angle, self.FunctionTab._down_arrow),
      self.FunctionTab(self.get_angle, "", "display"),
      self.FunctionTab(self.increment_angle, self.FunctionTab._up_arrow)
    ]

    anchor_interface.function_tabs = [
      self.FunctionTab(self.get_anchor, "", "display")
    ]
    end_interface.function_tabs = [
      self.FunctionTab(self.get_end, "", "display")
    ]

    return new_selection

  def delete(self):
    self.remove_interface()
    self.objects.remove(self)
    del self

  def check_select(self, screen, mouse_press, last_mouse_press, mouse_pos):

    if self.anchor == None or self.end == None:
      return

    minpos = [min(self.anchor[0], self.end[0]), min(self.anchor[1], self.end[1])]
    maxpos = [max(self.anchor[0], self.end[0]), max(self.anchor[1], self.end[1])]

    if mouse_press[0] == True and last_mouse_press[0] == False:
      if minpos[0] - 1 <= mouse_pos[0] and maxpos[0] + 1 >= mouse_pos[0] and minpos[1] - 1 <= mouse_pos[1] and maxpos[1] + 1 >= mouse_pos[1]:

        self.selected = True

        if self.interface != None:
          return

        self.create_interface()

      else:
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

  def remove_interface(self):
    self.Interface._children.remove(self.interface)
    self.interface = None

  def set_color(self, color):
    self.grid_color = color

  def get_length(self):
    return self.length

  def get_angle(self):
    return self.angle

  def increment_length(self):
    self.set_length(self.length + 10)

  def decrement_length(self):
    self.set_length(max(1, self.length - 10))

  def set_angle_0(self):
    self.set_angle(0)

  def increment_angle(self):
    self.set_angle(self.angle + 10)

  def decrement_angle(self):
    self.set_angle(self.angle - 10)

  def get_anchor(self):
    return self.anchor

  def get_end(self):
    return self.end

  def set_anchor(self, X, Y):
    self.anchor = [X, Y]
    obj = Line._base.copy()
    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]
    self.object = self.pygame.transform.rotate(
      self.pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def shift_anchor(self, X=0, Y=0):
    self.anchor[0] += X
    self.anchor[1] += Y
    obj = Line._base.copy()
    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]
    self.object = self.pygame.transform.rotate(
      self.pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def set_end(self, X, Y):
    dx = self.anchor[0] - X
    dy = self.anchor[1] - Y

    #self.end = [X, Y]

    self.set_length(math.sqrt((dx ** 2) + (dy ** 2)))

    if dy != 0:
      side = (dy/abs(dy))
    elif dx != 0:
      side = (dx/abs(dx))
    else:
      side = 1
    self.set_angle(math.degrees(math.acos(dx/max(1, self.length)) * side))

  def set_length(self, length):
    self.length = length
    obj = Line._base.copy()

    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]

    self.object = self.pygame.transform.rotate(
      self.pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def set_angle(self, angle=0, in_radians=False):

    if self.anchor == None:
      return

    obj = Line._base.copy()

    if in_radians:
      angle = math.degrees(angle)

    self.angle = angle

    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]

    self.object = self.pygame.transform.rotate(
      self.pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def set_grid_size(self, grid_size):
    self.grid_size = grid_size

  def _threaded_trace(self):
    
    if self.object == None or self.anchor == None or self.end == None:
      return

    draws = []

    # raytrace based
    for l in range(int(round(self.length, 2) * 100)):
      ray_x = self.anchor[0] - (math.cos(math.radians(self.angle)) * (l/100))
      ray_y = self.anchor[1] - (math.sin(math.radians(self.angle)) * (l/100))

      target_x = ray_x // self.grid_size
      target_y = ray_y // self.grid_size

      if (((target_x) * self.grid_size), ((target_y) * self.grid_size), self.grid_size, self.grid_size) not in draws:
        draws.append(
          (
            ((target_x) * self.grid_size),
            ((target_y) * self.grid_size),
            self.grid_size,
            self.grid_size
          )
        )

    self.draws = draws

  def trace(self, screen):

    if self.object == None or self.anchor == None or self.end == None:
      return

    """
    self.draws = []

    # raytrace based
    for l in range(int(round(self.length, 2) * 100)):
      ray_x = self.anchor[0] - (math.cos(math.radians(self.angle)) * (l/100))
      ray_y = self.anchor[1] - (math.sin(math.radians(self.angle)) * (l/100))

      target_x = ray_x // self.grid_size
      target_y = ray_y // self.grid_size

      if (((target_x) * self.grid_size), ((target_y) * self.grid_size), self.grid_size, self.grid_size) not in self.draws:
        self.draws.append((((target_x) * self.grid_size),
          ((target_y) * self.grid_size),
          self.grid_size,
          self.grid_size))
    """

    for draw in self.draws:
      #screen.fill(
      #  self.grid_color,
      #  draw
      #)

      x = Line._grid_object.copy()
      x.fill((self.grid_color))

      if len(self.grid_color) == 4:
        x.set_alpha(self.grid_color[3])

      x = self.pygame.transform.scale(x, (self.grid_size, self.grid_size))

      screen.blit(
        x, draw[0:2]
      )

  def update(self, screen, mouse_pos, mouse_press, last_mouse_press, mode):
    # global mode

    if self.object == None or self.end == None or self.anchor == None:
      return

    render_pos = (min(self.anchor[0], self.end[0]), min(self.anchor[1], self.end[1]))

    screen.blit(self.object, render_pos)

    screen.fill((255, 0, 0), (self.anchor[0]-1, self.anchor[1]-1, 3, 3))

    screen.fill((0, 0, 255), (self.end[0]-1, self.end[1]-1, 3, 3))

    if mode != "vertex edit":
      return

    if mouse_pos[0] <= self.anchor[0] + 5 and mouse_pos[0] >= self.anchor[0] - 5 and mouse_pos[1] <= self.anchor[1] + 5 and mouse_pos[1] >= self.anchor[1] - 5:

      if last_mouse_press[0] == False and mouse_press[0] == True:
        self.Grab(self, "anchor")

    elif mouse_pos[0] <= self.end[0] + 5 and mouse_pos[0] >= self.end[0] - 5 and mouse_pos[1] <= self.end[1] + 5 and mouse_pos[1] >= self.end[1] - 5:

      if last_mouse_press[0] == False and mouse_press[0] == True:
        self.Grab(self, "end")