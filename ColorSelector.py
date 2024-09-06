import re

from PIL import Image, ImageColor

from TextInput import TextInput

# 8 methods
class ColorSelector:
  open_panels = []

  _color_bar = None

  _font = None

  rgba_label = None
  hex_label = None

  @classmethod
  def init(cls, pygame):
    cls.pygame = pygame

    cls._color_bar = pygame.image.load("./resources/color_bar.png")
    cls._font = pygame.font.Font(pygame.font.get_default_font(), 8)
  
    cls.rgba_label = cls._font.render("RGB", True, (0, 0, 0))
    cls.hex_label = cls._font.render("HEX", True, (0, 0, 0))

  def __init__(self, x, y, return_to, initial_color=(0, 0, 0, 255)):
    """
    return_to needs to be a function that takes one argument of a tuple: (r, g, b [, a])
    """
    self.x = x
    self.y = y
    self.width = 265
    self.height = 75
    self.drawx = None
    self.drawy = None
    
    if "__call__" in dir(initial_color):
      initial_color = initial_color()

    self.return_to = return_to
    self.r = initial_color[0]
    self.g = initial_color[1]
    self.b = initial_color[2]
    
    if len(initial_color) == 4:
      self.a = initial_color[3]
    else:
      self.a = 255
    
    self.r_slider_selected = False
    self.g_slider_selected = False
    self.b_slider_selected = False
    self.a_slider_Selected = False
    self.hex_input_open = False
    self.rgb_input_open = False
    self.input_box = None

    ColorSelector.open_panels.append(self)

  def from_hex(self, hex_code):

    if " " in hex_code or "," in hex_code:
      self.from_rgb(hex_code)
      return
    if not hex_code.startswith("#"):
      hex_code = f"#{hex_code}"

    if (len(hex_code) not in [7, 9]):
      return
    self.from_rgb(f"{ImageColor.getrgb(hex_code)}")

  def from_rgb(self, rgb_code):
    self.rgb_input_open = False
    self.hex_input_open = False
    vals = re.findall("\\d+\\d?\\d?", rgb_code)

    if len(vals) == 4:
      self.r, self.g, self.b, self.a = vals
      self.r = int(self.r)
      self.g = int(self.g)
      self.b = int(self.b)
      self.a = int(self.a)

    elif len(vals) == 3:
      self.r, self.g, self.b = vals
      self.r = int(self.r)
      self.g = int(self.g)
      self.b = int(self.b)
      self.a = 255

  def _check_select(self, screen, mouse_press, last_mouse_press, mouse_pos):

    if self.input_box not in TextInput.open_panels:
      self.input_box = None
      self.rgb_input_open = False
      self.hex_input_open = False

    if self.drawx == None:
      self.drawx = max(0, min(self.x, screen.get_width() - self.width - 5))

    if self.drawy == None:
      self.drawy = max(0, min(self.y, screen.get_height() - self.height - 5))

    if mouse_press[0] == True and last_mouse_press[0] == False:

      # select color
      if mouse_pos[0] >= self.drawx + 4 and mouse_pos[0] <= self.drawx + 24 and mouse_pos[1] >= self.drawy + 59 and mouse_pos[1] <= self.drawy + 71:
        self.return_to((self.r, self.g, self.b, self.a))
        ColorSelector.open_panels.remove(self)
        del self
        return

      # cancel
      if mouse_pos[0] >= self.drawx + 34 and mouse_pos[0] <= self.drawx + 56 and mouse_pos[1] >= self.drawy + 59 and mouse_pos[1] <= self.drawy + 71:
        
        if self.hex_input_open or self.rgb_input_open:
          self.input_box.cancel()

        ColorSelector.open_panels.remove(self)
        del self
        return

      # rgb input box
      if mouse_pos[0] >= self.drawx + 59 and mouse_pos[0] <= self.drawx + 71 and mouse_pos[1] >= self.drawy + 59 and mouse_pos[1] <= self.drawy + 71 and not self.rgb_input_open:
        self.rgb_input_open = True
        self.input_box = TextInput(self.drawx + 60, self.drawy - 20, self.from_rgb)

      # hex input box
      if mouse_pos[0] >= self.drawx + 74 and mouse_pos[0] <= self.drawx + 96 and mouse_pos[1] >= self.drawy + 59 and mouse_pos[1] <= self.drawy + 71 and not self.hex_input_open:
        self.hex_input_open = True
        self.input_box = TextInput(self.drawx + 75, self.drawy - 20, self.from_hex)

      if mouse_pos[0] >= self.drawx + 4 and mouse_pos[0] <= self.drawx + 261:

        # red slider
        if mouse_pos[1] >= self.drawy + 19 and mouse_pos[1] <= self.drawy + 26:
          self.r_slider_selected = True

        else:
          self.r_slider_selected = False
          
        # green slider
        if mouse_pos[1] >= self.drawy + 29 and mouse_pos[1] <= self.drawy + 36:
          self.g_slider_selected = True

        else:
          self.g_slider_selected = False

        # blue slider
        if mouse_pos[1] >= self.drawy + 39 and mouse_pos[1] <= self.drawy + 46:
          self.b_slider_selected = True

        else:
          self.b_slider_selected = False

        # alpha slider
        if mouse_pos[1] >= self.drawy + 49 and mouse_pos[1] <= self.drawy + 56:
          self.a_slider_selected = True

        else:
          self.a_slider_selected = False

      else:
        self.r_slider_selected = False
        self.g_slider_selected = False
        self.b_slider_selected = False
        self.a_slider_selected = False

    if mouse_press[0] == False:
      self.r_slider_selected = False
      self.g_slider_selected = False
      self.b_slider_selected = False
      self.a_slider_selected = False

  def _update(self, screen, _ui_color, mouse_pos):
    
    # draw panel box
    screen.fill(
      _ui_color,
      (self.drawx, self.drawy, self.width, self.height)
    )

    # select color
    screen.fill(
      (0, 200, 20, 255),
      (self.drawx + 5, self.drawy + 60, 20, 10)
    )

    # cancel
    screen.fill(
      (250, 20, 0, 255),
      (self.drawx + 35, self.drawy + 60, 20, 10)
    )

    #rgb input box
    screen.fill(
      (120, 120, 120),
      (self.drawx + 60, self.drawy + 60, 20, 10)
    )
    screen.blit(
      ColorSelector.rgba_label,
      (self.drawx + 60, self.drawy + 60)
    )

    #hex input box
    screen.fill(
      (120, 120, 120),
      (self.drawx + 85, self.drawy + 60, 20, 10)
    )
    screen.blit(
      ColorSelector.hex_label,
      (self.drawx + 85, self.drawy + 60)
    )

    # slider bars
    # p = ColorSelector.open_panels[0]

    for x in range(256):
      screen.fill(
        (self.r, self.g, x, 255),
        (self.drawx + 5 + x, self.drawy + 40, 1, 5)
      )
      screen.fill(
        (self.r, x, self.b, 255),
        (self.drawx + 5 + x, self.drawy + 30, 1, 5)
      )
      screen.fill(
        (x, self.g, self.b, 255),
        (self.drawx + 5 + x, self.drawy + 20, 1, 5)
      )
      b = ColorSelector._color_bar.copy()
      b.fill((self.r, self.g, self.b))
      b.set_alpha(x)
      screen.blit(
        b,
        (self.drawx + 5 + x, self.drawy + 50)
      )
    
    if self.r_slider_selected:
      self.r = max(0, min(255, mouse_pos[0] - self.drawx + 5))

    if self.g_slider_selected:
      self.g = max(0, min(255, mouse_pos[0] - self.drawx + 5))

    if self.b_slider_selected:
      self.b = max(0, min(255, mouse_pos[0] - self.drawx + 5))

    if self.a_slider_selected:
      self.a = max(0, min(255, mouse_pos[0] - self.drawx + 5))

    # color display
    #screen.fill(
    #  (self.r, self.g, self.b),
    #  (self.drawx + 5, self.drawy + 5, 256, 10)
    #)
    disp = self.pygame.transform.scale(ColorSelector._color_bar, (256, 10))
    disp.fill((self.r, self.g, self.b))
    disp.set_alpha(self.a)
    screen.blit(disp, (self.drawx + 5, self.drawy + 5))
    

    #input boxes
    #screen.fill(
    #  (40, 40, 40),
    #  (self.drawx + 20, self.drawy + 5, 118, 10)
    #)
    #screen.fill(
    #  (40, 40, 40),
    #  (self.drawx + 143, self.drawy + 5, 118, 10)
    #)

  @classmethod
  def check_select(cls, screen, mouse_press, last_mouse_press, mouse_pos):
    for panel in cls.open_panels:
      panel._check_select(screen, mouse_press, last_mouse_press, mouse_pos)

  @classmethod
  def update(cls, screen, _ui_color, mouse_pos):
    for panel in cls.open_panels:
      panel._update(screen, _ui_color, mouse_pos)