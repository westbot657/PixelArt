
class Objects:

  def __init__(self, *args):
    self._objects = list(*args)

  def set(self, vals:list):
    self._objects = vals

  def remove(self, val):
    self._objects.remove(val)

  def append(self, val):
    self._objects.append(val)

  def insert(self, pos, val):
    self._objects.insert(pos, val)

  def clear(self):
    self._objects.clear()
  
  def pop(self, index):
    return self._objects.pop(index)
  
  def __getitem__(self, item):
    return self._objects[item]

  def __setitem__(self, key, value, /):
    self._objects[key] = value
  
  def __str__(self):
    return str(self._objects)

  def __repr__(self):
    return repr(self._objects)

  def __sizeof__(self):
    return self._objects.__sizeof__()

  def __iter__(self):
    return self._objects.__iter__()



