
# 5 methods
class FunctionTab:

  _right_arrow = None
  _up_arrow = None
  _left_arrow = None
  _x = None
  _trash = None
  _align = None
  _visible = None
  _invisible = None

  _save = None

  _add_line_end = None
  _add_line_start = None
  _remove_line_end = None
  _remove_line_start = None

  _polygon = None
  _rectangle = None
  _triangle = None
  _line = None
  _circle = None
  _arc = None

  _font = None

  @classmethod
  def init(cls, pygame):
    cls._right_arrow = pygame.transform.scale(pygame.image.load("./resources/arrow.png"), (4, 7))
    cls._down_arrow = pygame.transform.rotate(cls._right_arrow, -90)
    cls._up_arrow = pygame.transform.rotate(cls._right_arrow, 90)
    cls._left_arrow = pygame.transform.rotate(cls._right_arrow, 180)
    cls._x = pygame.image.load("./resources/x_button.png")
    cls._trash = pygame.image.load("./resources/trash.png")
    cls._align = pygame.image.load("./resources/align.png")
    cls._visible = pygame.image.load("./resources/visible.png")
    cls._invisible = pygame.image.load("./resources/invisible.png")
  
    cls._save = pygame.image.load("./resources/save.png")
  
    cls._add_line_end = pygame.image.load("./resources/add_line_end.png")
    cls._add_line_start = pygame.image.load("./resources/add_line_start.png")
    cls._remove_line_end = pygame.image.load("./resources/remove_line_end.png")
    cls._remove_line_start = pygame.image.load("./resources/remove_line_start.png")
  
    cls._polygon = pygame.image.load("./resources/polygon.png")
    cls._rectangle = pygame.image.load("./resources/rectangle.png")
    cls._triangle = pygame.image.load("./resources/triangle.png")
    cls._line = pygame.image.load("./resources/line.png")
    cls._circle = pygame.image.load("./resources/circle.png")
    cls._arc = pygame.image.load("./resources/arc.png")
  
    cls._font = pygame.font.Font(pygame.font.get_default_font(), 8)
  
  def __init__(self, func, surface, func_type="run-on-click", args=(), kwargs={}, func2=None, surface2=None, args2=(), kwargs2={}):
    """
    types: run-on-click, display, toggle
    """
    self.func = func
    self.args = args
    self.kwargs = kwargs
    self.toggle_state = None
    self.func2 = None
    self.surface2 = None
    self.args2 = None
    self.kwargs2 = None

    if func_type == "run-on-click":
      self.update = self.run_on_click_update

    elif func_type == "display":
      self.update = self.display_update

    elif func_type == "toggle":
      self.update = self.toggle_update
      self.toggle_state = False
      self.func2 = func2
      self.args2 = args2
      self.kwargs2 = kwargs2

      if isinstance(surface2, str):
        self.surface2 = FunctionTab._font.render(surface2, True, (0, 0, 0))

      else:
        self.surface2 = surface2

    if isinstance(surface, str):
      self.surface = FunctionTab._font.render(surface, True, (0, 0, 0))

    else:
      self.surface = surface

    self.width = self.surface.get_width() + 5

  def toggle_update(self, screen, x, y, _ui_color, mouse_pos, mouse_press, last_mouse_press):
    screen.fill(_ui_color, (x, y, self.width, 15))
    
    if self.toggle_state:
      screen.blit(self.surface2, (x+1, y+1))

    else:
      screen.blit(self.surface, (x+1, y+1))

    if x - 1 <= mouse_pos[0] and x + self.width + 1 >= mouse_pos[0] and y - 1 <= mouse_pos[1] and y + 16 >= mouse_pos[1]:

      if mouse_press[0] == True and last_mouse_press[0] == False:
        if self.toggle_state == False:
          self.func(*self.args, **self.kwargs)
          self.toggle_state = True
        
        else:
          self.func2(*self.args2, **self.kwargs2)
          self.toggle_state = False

  def run_on_click_update(self, screen, x, y, _ui_color, mouse_pos, mouse_press, last_mouse_press):

    screen.fill(_ui_color, (x, y, self.width, 15))
    screen.blit(self.surface, (x+1, y+1))
    if x - 1 <= mouse_pos[0] and x + self.width + 1 >= mouse_pos[0] and y - 1 <= mouse_pos[1] and y + 16 >= mouse_pos[1]:

      if mouse_press[0] == True and last_mouse_press[0] == False:
        self.func(*self.args, **self.kwargs)
    
  def display_update(self, screen, x, y, _ui_color, *args, **kwargs):
    
    self.surface = FunctionTab._font.render(str(self.func(*self.args, **self.kwargs)), True, (0, 0, 0))
    self.width = self.surface.get_width() + 2

    screen.fill(_ui_color, (x, y, self.width, 15))
    screen.blit(self.surface, (x+1, y+1))