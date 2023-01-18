from Polygon import Polygon
import math

class Triangle(Polygon):
  
    def __init__(self, X, Y, radius, _gs):
        super().__init__(X, Y, _gs)

        self.radius = radius
        self.type = "Triangle Object"

        p1 = (X + radius, Y)
        p2 = (X + (math.cos(math.radians(120)) * radius), Y + (math.sin(math.radians(120)) * radius))
        p3 = (X + (math.cos(math.radians(240)) * radius), Y + (math.sin(math.radians(240)) * radius))
        self.vertices[0].set_anchor(*p1)
        self.vertices[0].set_end(*p2)

        #self.add_vertice(*p2)
        self.add_vertice(*p3)
        self.add_vertice(*p1)

    def extend_config(self, config):

      config["kwargs"].update({"radius": self.radius})

      return config