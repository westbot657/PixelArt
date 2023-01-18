
# 10 methods
class Interface:
  _text = "Interface"
  _expanded = True
  _children = []
  _arrow = None
  _down_arrow = None
  _font = None
  _scroll_dist = 0

  @classmethod
  def init(cls, pygame):
    cls.pygame = pygame
    cls._arrow = pygame.transform.scale(pygame.image.load("./resources/arrow.png"), (4, 7))
    cls._down_arrow = pygame.transform.rotate(cls._arrow, -90)
    cls._font = pygame.font.Font(pygame.font.get_default_font(), 8)

  def __init__(self, text, parent=None, expanded=False):
    self.parent = parent
    self.children = []
    self.text = text
    self.expanded = expanded
    self.function_tabs = []

    if self.parent == None:
      Interface._children.append(self)
    
    elif self.parent == False:
      pass

    else:
      self.parent.children.append(self)

  def set_text(self, text):
    self.text = text

  def set_parent(self, parent):
    self.parent = parent

  def set_children(self, children):
    self.children = children

  def set_grid_size(self, grid_size):
    pass

  def check_select(self, screen):
    pass

  def trace(self, screen):
    pass

  def _update(self, screen, y, _ui_color, mouse_pos, mouse_press, last_mouse_press):
    text_surface = Interface._font.render(self.text, True, (0, 0, 0))

    w = text_surface.get_width()

    screen.fill(
      _ui_color,
      (10, y, 10 + w, 15)
    )

    screen.blit(text_surface, (20, y + 1))

    offset = 17

    if 9 <= mouse_pos[0] and 26 >= mouse_pos[0] and y - 1 <= mouse_pos[1] and y + offset + 1 >= mouse_pos[1]:

      if mouse_press[0] == True and last_mouse_press[0] == False:
        if self.expanded:
          self.expanded = False

        else:
          self.expanded = True

    Xoffset = w + 22
    for tab in self.function_tabs:
      tab.update(screen, Xoffset, y, _ui_color, mouse_pos, mouse_press, last_mouse_press)
      Xoffset += tab.width + 2

    if self.expanded == None:
      pass

    elif self.expanded:

      screen.blit(Interface._down_arrow, (12, y + 2))

      for c in self.children:
        height = c._update(screen, y + offset, _ui_color, mouse_pos, mouse_press, last_mouse_press)
        offset += height + 2

    else:
      screen.blit(Interface._arrow, (12, y + 2))

    return offset

  @classmethod
  def update(cls, screen, events, _ui_color, mouse_pos, mouse_press, last_mouse_press):

    text_surface = cls._font.render(cls._text, True, (0, 0, 0))

    w = text_surface.get_width()

    screen.fill(
      _ui_color,
      (10, 10 - cls._scroll_dist, w + 15, 15)
    )

    screen.blit(text_surface, (22, 15 - cls._scroll_dist))

    offset = 30 - cls._scroll_dist
    if cls._expanded:

      screen.blit(cls._down_arrow, (12, 12 - cls._scroll_dist))

      for c in cls._children:
        height = c._update(screen, offset, _ui_color, mouse_pos, mouse_press, last_mouse_press)
        offset += height + 2

    else:
      screen.blit(cls._arrow, (12, 12 - cls._scroll_dist))

    if 9 <= mouse_pos[0] and 26 >= mouse_pos[0] and 9 - cls._scroll_dist <= mouse_pos[1] and 26 - cls._scroll_dist >= mouse_pos[1]:

      if mouse_press[0] == True and last_mouse_press[0] == False:
        if cls._expanded:
          cls._expanded = False

        else:
          cls._expanded = True

    for event in events:
      if event.type == cls.pygame.MOUSEWHEEL:
        cls._scroll_dist -= event.y * 10

    #cls._scroll_dist = min(max(0, cls._scroll_dist), (offset - (30 - cls._scroll_dist) - screen.get_height()) )#- screen.get_height())
