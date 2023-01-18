
class Place:
  obj = None
  
  def __init__(self, obj):
    Place.obj = obj

  # Empty method for easy compatibility
  @classmethod
  def set_grid_size(cls, grid_size):
    pass

  @classmethod
  def check_select(cls, screen, mouse_press, last_mouse_press):
    if mouse_press[0] == True and last_mouse_press[0] == False and cls.obj != None:
      cls.obj()
      cls.obj = None

  # Empty method for easy compatibility
  @classmethod
  def trace(cls, screen):
    pass

  # Empty method for easy compatibility
  @classmethod
  def update(cls, screen):
    pass