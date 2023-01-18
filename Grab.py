
# 2 methods
class Grab:
  holding = []
  def __init__(self, line, point):
    Grab.holding.append([line, point])

  @classmethod
  def update(cls, mouse_pos, mouse_press, last_mouse_press):
    for obj in cls.holding:
      l = obj[0]
      if obj[1] == "anchor":
        n = l.end
        l.set_anchor(*mouse_pos)
        l.set_end(*tuple(n))

      else:
        l.set_end(*mouse_pos)

    if last_mouse_press != mouse_press:
      if mouse_press[0] == False:
        cls.holding = []