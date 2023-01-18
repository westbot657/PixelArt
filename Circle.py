from Arc import Arc

# 1 override method
# 1 method
class Circle(Arc):
  
  def __init__(self, X, Y, radius, _gs):

    super().__init__(X, Y, _gs)

    #self.set_anchor(x, y)
    self.set_radius(radius)
    self.set_curve(360)

  def extend_config(self, config):

    config["type"] = "Circle Object"
    config["kwargs"].update({"radius": self.radius})

    return config