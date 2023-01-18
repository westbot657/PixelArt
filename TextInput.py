
class TextInput:
  open_panels = []

  _font = None

  @classmethod
  def init(cls, pygame):
    cls.pygame = pygame

    cls._font = cls.pygame.font.Font(pygame.font.get_default_font(), 12)
  
  def __init__(self, x, y, return_to):
    self.x = x
    self.y = y
    self.return_to = return_to
    self.text = []
    self.text_surface = TextInput._font.render("", True, (0, 0, 0))
    TextInput.open_panels.append(self)

  def _check_select(self, screen):
    self.x = max(5, min(self.x, screen.get_width() - 5))
    self.y = max(5, min(self.y, screen.get_height() - 5))

  def cancel(self):
    if self in TextInput.open_panels:
      TextInput.open_panels.remove(self)

    del self

  def _update(self, screen, events):
    
    for event in events:

      if event.type == self.pygame.KEYDOWN:
        if event.key == self.pygame.K_BACKSPACE:
          if len(self.text) == 0:
            continue
          self.text.pop(-1)
          self.text_surface = TextInput._font.render("".join(self.text), True, (0, 0, 0))

        elif event.key == self.pygame.K_UP or event.key == self.pygame.K_DOWN or event.key == self.pygame.K_LEFT or event.key == self.pygame.K_RIGHT:
          pass
        
        elif event.key == self.pygame.K_RETURN:
          self.return_to("".join(self.text))
          TextInput.open_panels.remove(self)
          del self
          return

        elif event.key == self.pygame.K_ESCAPE:
          TextInput.open_panels.remove(self)
          del self
          return

        else:
          self.text.append(event.unicode)
          self.text_surface = TextInput._font.render("".join(self.text), True, (0, 0, 0))

    screen.fill(
      (255, 255, 255),
      (self.x, self.y, max(self.text_surface.get_width(), 5), self.text_surface.get_height())
    )
    screen.blit(
      self.text_surface, (self.x, self.y)
    )


  @classmethod
  def check_select(cls, screen):
    for panel in cls.open_panels:
      panel._check_select(screen)

  @classmethod
  def update(cls, screen, events):
    for panel in cls.open_panels:
      panel._update(screen, events)