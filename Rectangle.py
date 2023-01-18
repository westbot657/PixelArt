from Polygon import Polygon
import math

class Rectangle(Polygon):

  def __init__(self, X, Y, width, height, _gs, rotation=0):

    super().__init__(X, Y, _gs)
    self.type = "Rectangle Object"
    self.rotation = rotation
    self.width = width
    self.height = height
    
    x1 = self.anchor[0]
    y1 = self.anchor[1]

    x1 += math.cos(math.radians(self.rotation)) * (self.width/2)
    y1 += math.sin(math.radians(self.rotation)) * (self.width/2)

    x1 += math.cos(math.radians(self.rotation + 90)) * (self.height/2)
    y1 += math.sin(math.radians(self.rotation + 90)) * (self.height/2)

    self.vertices[0].set_anchor(x1, y1)
    self.vertices[0].set_length(self.width)
    self.vertices[0].set_angle(self.rotation)

    self.add_vertice_from_last(self.height, 90)
    self.add_vertice_from_last(self.width, 90)
    self.add_vertice_from_last(self.height, 90)

  def extended_interface(self, interface):
    interface.type = "Rectangle Object"

  def extend_config(self, config):

    config["type"] = "Rectangle Object"
    config["kwargs"].update(
      {"width": self.width, "height": self.height, "rotation": self.rotation}
    )

    return config