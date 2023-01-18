# Pixelator.py
# vector and bitmap art
# Weston Day 2021

import os
import math
import pygame
import json
import re

from threading import Thread
from PIL import Image, ImageColor

Screen = pygame.display.set_mode((625, 250))

##### Usage Guide:
# Drop down menu should be self-explanatory
# menu can scroll if it goes off screen

# Menus:
# [> Object]
# [value] [modifiers/value displays]
#
# [> value group] [mods/disps]
# [sub-value] [mods/disps]
#
# click arrows to collapse/open areas

# Function Symbols:
# trash can  -means delete geometry object
# x          -means remove menu part (object is not
#             deleted, and menu can be opened be
#             re-selecting the object)
# save icon  -saves a shapes values to a json file
#             that you name (opens a very simple text box)

# Geometry Interaction:
#
# mode needs to be set to "vertex edit" in order to modify shapes
#
# Drag Tabs:
# Magenta:    Movement
# Yellow:     Rotation
# Orange:     Scale
# Light blue: width/height scale
# Dark blue:  verticle/horizontal scale

# Console Commands:
# to_image(<polys>)    make an image from a list of geometry
#                       objects.
#                       Using `objects` as <polys> will use all
#                       objects that are on screen
# clear()              Deletes all objects
# get(<index>)         Returns a geometry object
# 

# Interaction Classes:
# Polygon                      Base class for all geometry
# Triangle (Polygon)
# Rectangle (Polygon)
# Arc (Polygon)
# Circle (Arc)
# Line                         Not really meant for direct usage
# Animation                    Pretty Complicated, Explained later
#
# Internal Classes: (leave thes alone)
# mouse_grid
# TextInput
# ColorSelector
# FunctionTab
# Interface
# Place
# Grab

# Interaction Methods:
# clear()                Delete all geometry objects in the objects
#                         list
# animate(poly, anim)    poly is geometry object, anim is string
#                         working anim args: "rotate", "scale"
# set_mode(m)            Change the editor mode. default "selection"
#                         you can only modify geometry if mode is
#                         "vertex edit"
# to_image(polys)        Create png of all shapes in `polys`
# get(i)                 Get geometry object from the objects list
#                         at index `i`
# load_pattern(pattern)  Load a shape from a json file that has
#                         `pattern` in the file name (loads all
#                         files that contain `pattern`)
# single_thread_tracers  switch all fill math to run on one thread
# multi_thread_tracers   switch all fill math to run on individual
#                         threads
#
# Internal Methods: (don't use these)
# gs_down
# gs_disp
# gs_up
# hide_lines
# show_lines
# show_grids
# hide_grids
# show_env_grids
# hide_env_grids
# get_mode
# place_polygon
# place_line
# place_rectangle
# place_triangle
# place_arc
# place_circle
# TraceLoop
# InputLoop

# Variables:
# mode                    The editing mode
# modes                   All editing modes (not all are implemented)
# objects                 All geometry objects on the screen
# rotate_anim             Pre-defined animation object for easy use
#
# Internal Variables: (please read only, do not modify through console)
# events                  Pygame events
# last_mouse_press        Previous mouse button state
# mouse_press             Current mouse button state
# mouse_pos               Mouses position
# _gs                     Grid Size
# show_line               Whether to show geometry lines
# show_grid               Whether to show geometry fill
# show_environment_grid   Wheteher to show grid lines
# running                 set to False to stop the program*
#
# Functionality Variables: (class instances for easier usability,
#                           leave these alone)
# image_data
# files
# ui
# main_interface
# gs
# gsdown
# gsdisp
# gsup
# _env_grids
# _grids
# _lines
# create_interface
# split_trace_threads
# TraceThread
# InputThread

# Polygon Usage:
# Polygon(X, Y)
#
# Methods:
# .move(x, y)
# .move_to(x, y)
# .rotate(a)                   Change rotation be angle
# .rotate_to(a)                Rotate to specified angle
# .rotate_towards(x, y)        Rotate to face position (x, y)
# .set_scale(x)
# .set_verticle_scale(x)
# .set_horizontal_scale(x)
# .set_width_scale(x)
# .set_height_scale(x)
# .save_config()               Returns save data
# .save(n)                     Save config data to file n
# .delete()
# .snap()                      Snaps the object to the grid
# .set_color((r, g, b [, a]))  Change the bitmap coloring
# .set_anchor(x, y)            Changes the origin of a shape, but
#                               doesn't move the shape
# .history()                   See the history of the shape, history
#                               doesn't include changes to lines.
# .undo()                      A bit buggy, doesn't undo changes to
#                               lines
# .redo()                      A bit buggy

# Arc Usage:
# Arc()
#
# Methods:
# .set_curve(a, s)             Regeneratess lines, goes around `a`
#                               degrees in `s` steps.
#                               with (360, 360//x) as args,
#                               generates shape with x sides
#                               (although doesn't always connect
#                               back to start properly)
#####


# create resources if needed
image_data = [
  {
    "file": "./resources/add_line_end.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x7fIDAT8O\xad\x92Q\x0e\xc0 \x08C\xcb\xfd\x0f\xdd\x05\r\x93i\xc9t\x19\x9f\xca\x83\x160\x10\x84\xc1\xa0\xc2\xff"D\x8e5\xd8C\x15\xd8\x86U\x81m8:g@z\x19*\xbb\xec,\xf9\x04&@s\xc7\x11\'0\xd0\x06\xf6q\xda\xbd\xa3.\xf0:\xb0\x1f\xe0\xba\xbb\xbe\x1e\x02f\xd9k\xed}\x14 I\xc7\x1a7\x0fj)\xe0\xd9\x9e\x9b\xa1q\xb1OY7\x1cP\xb9\t\xfdA\xf7\xa3T-\xee\xf5~\xab\xb3\x9c\xde/\x0b-8\x10\x15\x1f~\xa2\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/add_line_start.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x86IDAT8O\xa5\x92Y\x12\xc0 \x08C\xc3\xfd\x0f\x9d\x0e\xad(\xe0>\xf5\xcb\x85\xb0\xbc(\xb0E\x10\x02\xa9g\xdd\xe8\x9d\xad\xfc\x06\x94`\x0b\xba\x16\xaf\xb2_W\xf6\x820\x83;\x94\x0e\xdb\x8c6\xf3\x9d\x98\x04$&\x99UL\xf0T\xa4D#e\xef\xc0\x96\xf6,\xc1\x11\xb0\x9f\xe2\xefK\xcc\xdaO\x0c\x08P\x02\xa831IB\xe4\x03\x9cAu\xd55Zc\xbd\xa81\x8c-U\xb1\x89V\xa3\x0c,z}\x1fu\xd5\xb9?\xf6w\xf7I\xca\xfb\x03\xdb\x1e8\x10:o\x1e\xae\x00\x00\x00\x00IEND\xaeB`\x82'
  },
  {
    "file": "./resources/align.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\xb5IDAT8O\xa5\x93\xeb\x11\x84 \x0c\x84C#V\x92J(0\x95\xa4\x12\x1a\xc1Y\x86e\xa2<\xeen\xce?\xca\x9a/\xb2\x1bI\xf2\xc5\x95s\xaef\x96\xde\xa5\x93\xc0\x02\x00x.\xa5\xc8u]\x02\x98\x1a\x1b-aUm\xa0\xbb\x8b\xaa6\x18M\xba\xd6\x9a\xa0\xc1\nn\xa0\x88\xe0]\x05\x8c&\xd4\xd0\x98;y\xc3,\xa6~\\Op\xcey\xe4bfm\x07!\xb0\x1a\xdf?`z%\xed\xee\t\x1a\xef1mh\x11\xa6\xd7\xe1\x0f\x9e\xe9=\x82\xf8\xfa2\xb0\x18\x08\x80\xd3z\x1bX\xf79F\xd5g\xfb\x08p\x82\xb1\xcd\xdd\x9c\xfb\xc8\x06\xf3\xf3\x9c\xa3\xf7\xed\xef\xd9\x8b\x18\xd8\xf2\x04|\x82\x8f\xc7\xe6/\xf8\x06\xcf\xbfz\x1d\xe2\xb5Je\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/arc.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00LIDAT8O\xc5\x921\x0e\x00 \x08\x03\xdb\xff?\xbaF\x06t1\x06\x1a#\xfb\xf5R\x800\x86EV\x00\x92\xa9\xc2\xd3\x95\x01\x1d8\x03\xbe\xc0a\xef\x9a\xef\xb0 \x11<\t\x1e\x9a\xf7\x1f\x90 r\xdd\xd8\xe9\x1c\xb7\xee.\xcc\x82\xa3Q\xd7\xec\xc3\x03ga\x11\x0bF1uX\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/arrow.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08\x00\x00\x00\x0f\x08\x06\x00\x00\x00\xd9\n\x8e3\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00IIDAT(S\x9d\xd1Q\n\x00 \x08\x03\xd0y\xffC\x17\nE\xd6f\x94\xbf>\x84M\x03\xd0\x00\x18\xc4\xf8\xc2\x81\x0fE+\xa0h\x07\x07b !\x05&\xaa@\xa0\x1b\x88h#&k\xa2\xbc\x10\xbd|\xa5H\x8d>5Y\xfeB~\xb3\x03Ld\x0f\x0fa\xbd\x0b\xa3\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/circle.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00gIDAT8O\xb5SI\x0e\x00!\x08+\xff\x7ft\'L\x82\xb2\x1d$FO\x06Z\x1aK\x15\xf4\x87MYr-\x17\x8cT\x80\x00J\xcf\x83\xb4\xd9\x91\xb2\xe0\xc2\x19\xf8\x94h\x83~\xfc5y\xaa\xba\xd4U\xf9\r\x99 e?\xad\x18\xf7N\xd9K\x91\xa0HX%\xaf\xddV\x81\xa9ia\xcf\x93\x01%a>9z\x1fg;\xf8s\xf2\xab>9\xa0"\x0bh\xb2\x13\x0c\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/color_bar.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x05\x08\x06\x00\x00\x00\x84\x84\x86\x9f\x00\x00\x00\x14IDATx\x9cc```\xf8\xcf\xc4\xc0\xc0\xc0\x80F\x00\x00\x15h\x01\x08\x8d\xef\x99\xd0\x00\x00\x00\x00IEND\xaeB`\x82'
  },
  {
    "file": "./resources/invisible.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00AIDAT(Scd``\xf8\xcf\x00\x01\x8cP\x1a\x9d\x02\xcb\x83$a\n\xb1)\x86\xcb\xc1LAV\x8c\xcd`F\x92\x14\x82L\xc3\xa5\x01.\x0es#Q\nAn\xa2\xbe\x1ba>E\x0fK\x94\xe0!*\xc0\x01\xb0\xfa\x12\x05\x02\xb2*j\x00\x00\x00\x00IEND\xaeB`\x82'
  },
  {
    "file": "./resources/line_color.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\rIDAT\x18Wc`\xf8\xcf\xf0\x1f\x00\x04\x01\x01\xff^.\xe1\xa5\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/line.png",
    "data": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00QIDAT8O\xad\x93A\n\x00 \x08\x04\xf5\xff\x8f.<\x04\x85\x9a\xbb\x99g\xc7\x1dDU\x1a\xa5\rV\xbe\xc0C\x84\x1f\xb4'\xdb\x00+\xd8&j\x84-\xb2\x14\xc8\xa2R\xbcZT\xb0\xed \xb5@\xe0u\n\xce\x82\x81\x9d\x05\x0b\x1f\x16\xaf0w\x10\xd1\x0f\xb4\x92'0\xe7\t\x10\x04\x9f\x9cG\x00\x00\x00\x00IEND\xaeB`\x82\x00\x00"
  },
  {
    "file": "./resources/polygon.png",
    "data": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00mIDAT8O\x95R\xd1\x12\xc0 \x08\x82\xff\xffhv\xed\xae]\x99\xa4\xeb\xad\x02A\x94\xe8\x1d\x01`\x84\x1e\x0fI\xad\x948p7\xf2 ]1\x8el\xd5Vg\x19\xb9E\x8c\x96J\x9b.\xb0\xb6Z\xb4m\x15\x05\x89\xa0\ru\xfd\x98E\xaa)|\xe2\xb7\xb4'\xe8\xc5H\x10\xb9\x8f\xb6\xbb$[\xa1\xf4Rl\xea\xd1\x96\x9bsV\xc7\xee\xf6\xef\xb0\xda\xa9\xbav\x1eg\xaf\x14\x10\xf1C\x8e\xf7\x00\x00\x00\x00IEND\xaeB`\x82\x00"
  },
  {
    "file": "./resources/rectangle.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00tIDAT8O\xa5\x92A\x0e\xc0 \x08\x04\x97\xff?z\x1bIi)\x82\xd8\xe8Q\x19\xd9\x0c\x08\x0e\x8el\xb0\x04\x90\xd6u\xb0\x81\xe9\x07\x15<\x8a\xc7\xf1\xef\xd3]\x06\x971\xef\x0f\x9f\xf7\x08w\xa0)\xd2:\x83\xb3\x98 Hyk\xa2[\x0ex\xb7\x9b\xef\xaa>|\xe7\xd2<\t\x8a\xa8\xbcO\xa3hs5\xba)a&\xac\x1d\x91\xe5_\xcd\xb9\xf5\xf1+f\xd4\xdd\xad\xe7r\xf5\x8f\xe0\x0b\x9c\xca\x1c\x0f\xdc\xf2\xb2\x15\x00\x00\x00\x00IEND\xaeB`\x82'
  },
  {
    "file": "./resources/remove_line_end.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00lIDAT8O\xbd\x92Q\x0e\x800\x08C\xcb\xfd\x0f]S\xb4\x86\xb8\xb9(&\xf2\xcd+-\x10\x04\x18@\xa0Q!X\\G\xe0\x84;\x02\xc3d;Y\xa5\xb0\xcb\x84\xab\xe5\xff`\xec\x0b\xebm\xfb\xc8\xd6\x12\xf0\xc4O\xb0\x0c\xbc\x10 \x81\x88\x9a\xf5\tL\x92\xc2\x92\xbb.j\x10P\xb7z+\xe4\x1f\xb8\x85\r\xad.19Q\xe6\x99\xb9\x1a\x9e\xaeu_\xabl\x11\xfb,\x100\xa1\xfc\xd8\x00\x00\x00\x00IEND\xaeB`\x82\x00\x00'
  },
  {
    "file": "./resources/remove_line_start.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00|IDAT8O\xad\x92\xdb\x0e\x80 \x0cC\xbb\xff\xff\xe8\x9a\x015\x93\x8b2\xa2/\xc4d\xa7t-\x86\xf6\x11\xa0\x01\xa6\xff\x9d\xb3\x0c;\xe8g\x1a\x16x\x04\xf77G\xb1\x95u9\xbcw\xd4\xceI\x98\x04\xec!\xf2\x15V\xbc\xd9\xc3J\xa5,qAG\x02\xbf\xc0-\xf4=\xfb\n7\xee\xbac\x9d$aV\x03\xee\x83\x1a\x04|\xdag#\xd4\x07\x16\x9ex\x15\x14\xf4\xd6\xc4\xa4\xa2\xd2\xfb\xcc\xd5P\xffQ\xbfR\xb9\x00\xe1\xec,\x10\xb3\x17X9\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/save.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00VIDAT8Ocd```\x10\xe9\x10\xf8\xaf\xb0F\x05\xc4\xc4\x00\x0fB\xee\x80\xc5\xdeT|`D\x97d\x04i\x04\t\x12\xd2\x8c\xcd\x00\x924\xa3\x1b@\xb2fd\x03\xe0\x9a\xb1z\x18\x8f (\x0c\xc8\xd6\x0c2w\xc4k\xc6\x95P\x90\x03\x1d\x96\xe20\x02l\x88j&5\x95\x01\x00\xe7\x1a<\xbe\x9f\x0f\x14\xc4\x00\x00\x00\x00IEND\xaeB`\x82'
  },
  {
    "file": "./resources/trash.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00dIDAT8O\xa5\x92\xdb\n\x00 \x08C\xeb\xff?\xbaP(L7\r\xec\xad\xecl\xde\xe6h\x9c\x99\xb0\xcb\xc4\xe0?\x06\x0bhc\xfe\xae\xba\x1e\xb6n,\xa9\xcb\x94\xea@\xe1f\xe1\xe1\xdf\xf6)\xc7\x9c\xb3\x9a\xa1\xb3\x88\x9d\x00\x83\x9fw\xd40yk\xc1,\x8b\xd4\x19A\xac\x940\xe76|\x04\xfc\xd8\xc26f\xbb]\xce\xbc\x05o9u \x10L\xee\x99\x90\x00\x00\x00\x00IEND\xaeB`\x82\x00'
  },
  {
    "file": "./resources/triangle.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00xIDAT8O\xb5\x92\xdb\x0e\x800\x08C\xe9\xff\x7f4\x06#8nCc\xdc\x8b\xc9\xe8)\x95\x01\x9a\x0f_\x12Di\xba\x08\x02\x01E\xa3_W\xde\xc1\x11H\x06\xbf\xc0e\xcc\x18\xbf\xea\xdc\x81\xf2\xbf\xae\x16aWdb\x06a\xd5\xb4\xf0\xae\xe3:e\xd3\xb5\xaeN\xcd\xc4\xc0\xf9d.z\xba\x98w\xe66\xd0\x05X\x99iq\xac{7\xed*@\x1a\xee\x93.j\xa4;n\xc6o\xe0\x94\xe6\x13|\x00\xfa\xba\x1e\x0e"X\x88\xc7\x00\x00\x00\x00IEND\xaeB`\x82\x00\x00'
  },
  {
    "file": "./resources/visible.png",
    "data": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x009IDAT(Scd \x120\x12\xa9\x8e\x01Y\xe1\x7f\x1c\x9a\xc0j`\nA\x8ap\x99\x0e\x96\x03I\xa2+\x82\x99\x8cb\x1bI\nAN \xcaj\x98\x1f\x88\xf2\x0c\xc1P":\x1c\x01\xab%\x0c\tR\xb5yJ\x00\x00\x00\x00IEND\xaeB`\x82\x00\x00'
  },
  {
    "file": "./resources/x_button.png",
    "data": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x07\x00\x00\x00\x07\x08\x06\x00\x00\x00\xc4RW\xd3\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00.IDAT\x18Wcd``\xf8\xcf\x00\x01\x8cP\x1aD\x81\xc5@\x020I\x0c>L5\xb2\x02\x98\x01\x8c\x18F![AP'^;q\xba\x16\x00z_\x0b\x04\xf24\xc6\xf9\x00\x00\x00\x00IEND\xaeB`\x82\x00"
  }
]

if "./resources" not in [f.path for f in os.scandir()]:
  os.mkdir("./resources")

files = [f.path for f in os.scandir("./resources")]
for img_dat in image_data:
  if img_dat["file"] not in files:
    open(img_dat["file"], "wb+").write(img_dat["data"])

#os.chdir(str(os.path.realpath(__file__)).replace("Pixelator.py", ""))

mode = "selection"
modes = [
  "selection",
  "vertex edit",
  "vector erase",
  "bitmap draw",
  "bitmap erase",
  # "bitmap fill"
]
pygame.font.init()
objects = []
events = []
ui = []
last_mouse_press = [False, False, False]
mouse_press = None
mouse_pos = None

class TextInput:
  open_panels = []

  _font = pygame.font.Font(pygame.font.get_default_font(), 12)

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

  def _update(self, screen):
    
    for event in events:

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_BACKSPACE:
          if len(self.text) == 0:
            continue
          self.text.pop(-1)
          self.text_surface = TextInput._font.render("".join(self.text), True, (0, 0, 0))

        elif event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
          pass
        
        elif event.key == pygame.K_RETURN:
          self.return_to("".join(self.text))
          TextInput.open_panels.remove(self)
          del self
          return

        elif event.key == pygame.K_ESCAPE:
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
  def update(cls, screen):
    for panel in cls.open_panels:
      panel._update(screen)

class ColorSelector:
  open_panels = []

  _color_bar = pygame.image.load("./resources/color_bar.png")

  _font = pygame.font.Font(pygame.font.get_default_font(), 8)

  rgba_label = _font.render("RGB", True, (0, 0, 0))
  hex_label = _font.render("HEX", True, (0, 0, 0))

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

    self.from_rgb(f"{ImageColor.getrgb(hex_code)}")

  def from_rgb(self, rgb_code):
    self.rgb_input_open = False
    self.hex_input_open = False
    vals = re.findall("\d+\d?\d?", rgb_code)

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

  def _check_select(self, screen):

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

  def _update(self, screen):
    
    # draw panel box
    screen.fill(
      (80, 80, 80, 255),
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
    disp = pygame.transform.scale(ColorSelector._color_bar, (256, 10))
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
  def check_select(cls, screen):
    for panel in cls.open_panels:
      panel._check_select(screen)

  @classmethod
  def update(cls, screen):
    for panel in cls.open_panels:
      panel._update(screen)


class FunctionTab:

  _right_arrow = pygame.transform.scale(pygame.image.load("./resources/arrow.png"), (4, 7))
  _down_arrow = pygame.transform.rotate(_right_arrow, -90)
  _up_arrow = pygame.transform.rotate(_right_arrow, 90)
  _left_arrow = pygame.transform.rotate(_right_arrow, 180)
  _x = pygame.image.load("./resources/x_button.png")
  _trash = pygame.image.load("./resources/trash.png")
  _align = pygame.image.load("./resources/align.png")
  _visible = pygame.image.load("./resources/visible.png")
  _invisible = pygame.image.load("./resources/invisible.png")
  #_add_line = pygame.image.load("./resources/add_line.png")

  _save = pygame.image.load("./resources/save.png")

  _add_line_end = pygame.image.load("./resources/add_line_end.png")
  _add_line_start = pygame.image.load("./resources/add_line_start.png")
  _remove_line_end = pygame.image.load("./resources/remove_line_end.png")
  _remove_line_start = pygame.image.load("./resources/remove_line_start.png")

  _polygon = pygame.image.load("./resources/polygon.png")
  _rectangle = pygame.image.load("./resources/rectangle.png")
  _triangle = pygame.image.load("./resources/triangle.png")
  _line = pygame.image.load("./resources/line.png")
  _circle = pygame.image.load("./resources/circle.png")
  _arc = pygame.image.load("./resources/arc.png")

  _font = pygame.font.Font(pygame.font.get_default_font(), 8)

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

  def toggle_update(self, screen, x, y):
    screen.fill((100, 100, 100), (x, y, self.width, 15))
    
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

  def run_on_click_update(self, screen, x, y):

    screen.fill((100, 100, 100), (x, y, self.width, 15))
    screen.blit(self.surface, (x+1, y+1))
    if x - 1 <= mouse_pos[0] and x + self.width + 1 >= mouse_pos[0] and y - 1 <= mouse_pos[1] and y + 16 >= mouse_pos[1]:

      if mouse_press[0] == True and last_mouse_press[0] == False:
        self.func(*self.args, **self.kwargs)
    
  def display_update(self, screen, x, y):
    
    self.surface = FunctionTab._font.render(str(self.func(*self.args, **self.kwargs)), True, (0, 0, 0))
    self.width = self.surface.get_width() + 2

    screen.fill((100, 100, 100), (x, y, self.width, 15))
    screen.blit(self.surface, (x+1, y+1))

class Interface:
  _text = "Interface"
  _expanded = True
  _children = []
  _arrow = pygame.transform.scale(pygame.image.load("./resources/arrow.png"), (4, 7))
  _down_arrow = pygame.transform.rotate(_arrow, -90)
  _font = pygame.font.Font(pygame.font.get_default_font(), 8)
  _scroll_dist = 0

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

  def _update(self, screen, y):
    text_surface = Interface._font.render(self.text, True, (0, 0, 0))

    w = text_surface.get_width()

    screen.fill(
      (100, 100, 100),
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
      tab.update(screen, Xoffset, y)
      Xoffset += tab.width + 2

    if self.expanded == None:
      pass

    elif self.expanded:

      screen.blit(Interface._down_arrow, (12, y + 2))

      for c in self.children:
        height = c._update(screen, y + offset)
        offset += height + 2

    else:
      screen.blit(Interface._arrow, (12, y + 2))

    return offset

  @classmethod
  def update(cls, screen):

    text_surface = cls._font.render(cls._text, True, (0, 0, 0))

    

    w = text_surface.get_width()

    screen.fill(
      (100, 100, 100),
      (10, 10 - cls._scroll_dist, w + 15, 15)
    )

    screen.blit(text_surface, (22, 15 - cls._scroll_dist))

    offset = 30 - cls._scroll_dist
    if cls._expanded:

      screen.blit(cls._down_arrow, (12, 12 - cls._scroll_dist))

      for c in cls._children:
        height = c._update(screen, offset)
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
      if event.type == pygame.MOUSEWHEEL:
        cls._scroll_dist -= event.y * 10

    cls._scroll_dist = min(max(0, cls._scroll_dist), (offset - (30 - cls._scroll_dist) - screen.get_height()) )#- screen.get_height())

_gs = 8
def gs_down():
  global _gs
  _gs -= 1
  for obj in objects:
    obj.set_grid_size(_gs)

def gs_disp():
  global _gs
  return _gs

def gs_up():
  global _gs
  _gs += 1
  for obj in objects:
    obj.set_grid_size(_gs)

class Place:
  obj = None

  def __init__(self, obj):
    Place.obj = obj

  @classmethod
  def set_grid_size(cls, grid_size):
    pass

  @classmethod
  def check_select(cls, screen):
    if mouse_press[0] == True and last_mouse_press[0] == False and cls.obj != None:
      cls.obj()
      cls.obj = None

  @classmethod
  def trace(cls, screen):
    pass

  @classmethod
  def update(cls, screen):
    pass

ui.append(Place)

class Grab:
  holding = []
  def __init__(self, line, point):
    Grab.holding.append([line, point])

  @classmethod
  def update(cls):
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

class Line:

  _base = pygame.image.load("./resources/line_color.png")
  _angle_marker = _base.copy().fill((255, 255, 0))
  _grid_object = _base.copy()
  def __init__(self, *, queue=True):
    self.anchor = None
    self.end = None
    self.angle = 0
    self.length = 10
    self.width = 1
    self.grid_offset = (0, 0)
    self.grid_size = 20
    self.object = Line._base.copy()
    self.grid_color = (0, 0, 0)
    self.selected = False
    self.angle_marker = Line._angle_marker.copy()
    self.interface = None
    self.draws = []
    self.angle_selected = False
    if queue:
      objects.append(self)

  def create_interface(self, parent=None):
    new_selection = Interface("Line Object", parent=parent)
    self.interface = new_selection
    length_interface = Interface("Length", new_selection, None)
    angle_interface = Interface("Angle", new_selection, None)
    anchor_interface = Interface("Anchor", new_selection, None)
    end_interface = Interface("End", new_selection, None)

    if parent == None:
      new_selection.function_tabs = [
        FunctionTab(self.remove_interface, FunctionTab._x),
        FunctionTab(self.delete, FunctionTab._trash)
      ]

    length_interface.function_tabs = [
      FunctionTab(self.decrement_length, FunctionTab._down_arrow),
      FunctionTab(self.get_length, "", "display"),
      FunctionTab(self.increment_length, FunctionTab._up_arrow)
    ]

    angle_interface.function_tabs = [
      FunctionTab(self.set_angle_0, "set 0"),
      FunctionTab(self.decrement_angle, FunctionTab._down_arrow),
      FunctionTab(self.get_angle, "", "display"),
      FunctionTab(self.increment_angle, FunctionTab._up_arrow)
    ]

    anchor_interface.function_tabs = [
      FunctionTab(self.get_anchor, "", "display")
    ]
    end_interface.function_tabs = [
      FunctionTab(self.get_end, "", "display")
    ]

    return new_selection

  def delete(self):
    self.remove_interface()
    objects.remove(self)
    del self

  def check_select(self, screen):

    if self.anchor == None or self.end == None:
      return

    minpos = [min(self.anchor[0], self.end[0]), min(self.anchor[1], self.end[1])]
    maxpos = [max(self.anchor[0], self.end[0]), max(self.anchor[1], self.end[1])]

    if mouse_press[0] == True and last_mouse_press[0] == False:
      if minpos[0] - 1 <= mouse_pos[0] and maxpos[0] + 1 >= mouse_pos[0] and minpos[1] - 1 <= mouse_pos[1] and maxpos[1] + 1 >= mouse_pos[1]:

        self.selected = True

        if self.interface != None:
          return

        self.create_interface()

      else:
        self.selected = False

    if self.selected:
      screen.fill(
        (0, 255, 0),
        (minpos[0], minpos[1], maxpos[0] - minpos[0], 1)
      )
      screen.fill(
        (0, 255, 0),
        (minpos[0], minpos[1], 1, maxpos[1] - minpos[1])
      )
      screen.fill(
        (0, 255, 0),
        (maxpos[0], minpos[1], 1, maxpos[1] - minpos[1])
        )
      screen.fill(
        (0, 255, 0),
        (minpos[0], maxpos[1], maxpos[0] - minpos[0], 1)
      )

  def remove_interface(self):
    Interface._children.remove(self.interface)
    self.interface = None

  def set_color(self, color):
    self.grid_color = color

  def get_length(self):
    return self.length

  def get_angle(self):
    return self.angle

  def increment_length(self):
    self.set_length(self.length + 10)

  def decrement_length(self):
    self.set_length(max(1, self.length - 10))

  def set_angle_0(self):
    self.set_angle(0)

  def increment_angle(self):
    self.set_angle(self.angle + 10)

  def decrement_angle(self):
    self.set_angle(self.angle - 10)

  def get_anchor(self):
    return self.anchor

  def get_end(self):
    return self.end

  def set_anchor(self, X, Y):
    self.anchor = [X, Y]
    obj = Line._base.copy()
    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]
    self.object = pygame.transform.rotate(
      pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def shift_anchor(self, X=0, Y=0):
    self.anchor[0] += X
    self.anchor[1] += Y
    obj = Line._base.copy()
    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]
    self.object = pygame.transform.rotate(
      pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def set_end(self, X, Y):
    dx = self.anchor[0] - X
    dy = self.anchor[1] - Y

    #self.end = [X, Y]

    self.set_length(math.sqrt((dx ** 2) + (dy ** 2)))

    if dy != 0:
      side = (dy/abs(dy))
    elif dx != 0:
      side = (dx/abs(dx))
    else:
      side = 1
    self.set_angle(math.degrees(math.acos(dx/max(1, self.length)) * side))

  def set_length(self, length):
    self.length = length
    obj = Line._base.copy()

    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]

    self.object = pygame.transform.rotate(
      pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def set_angle(self, angle=0, in_radians=False):

    if self.anchor == None:
      return

    obj = Line._base.copy()

    if in_radians:
      angle = math.degrees(angle)

    self.angle = angle

    end_x = self.anchor[0] - (
      math.cos(math.radians(self.angle)) * self.length
    )
    end_y = self.anchor[1] - (
      math.sin(math.radians(self.angle)) * self.length
    )

    self.end = [end_x, end_y]

    self.object = pygame.transform.rotate(
      pygame.transform.scale(
        obj, 
        (self.length, self.width)
      ),
      -self.angle
    )

  def set_grid_size(self, grid_size):
    self.grid_size = grid_size

  def _threaded_trace(self):
    
    if self.object == None or self.anchor == None or self.end == None:
      return

    draws = []

    # raytrace based
    for l in range(int(round(self.length, 2) * 100)):
      ray_x = self.anchor[0] - (math.cos(math.radians(self.angle)) * (l/100))
      ray_y = self.anchor[1] - (math.sin(math.radians(self.angle)) * (l/100))

      target_x = ray_x // self.grid_size
      target_y = ray_y // self.grid_size

      if (((target_x) * self.grid_size), ((target_y) * self.grid_size), self.grid_size, self.grid_size) not in draws:
        draws.append(
          (
            ((target_x) * self.grid_size),
            ((target_y) * self.grid_size),
            self.grid_size,
            self.grid_size
          )
        )

    self.draws = draws

  def trace(self, screen):

    if self.object == None or self.anchor == None or self.end == None:
      return

    """
    self.draws = []

    # raytrace based
    for l in range(int(round(self.length, 2) * 100)):
      ray_x = self.anchor[0] - (math.cos(math.radians(self.angle)) * (l/100))
      ray_y = self.anchor[1] - (math.sin(math.radians(self.angle)) * (l/100))

      target_x = ray_x // self.grid_size
      target_y = ray_y // self.grid_size

      if (((target_x) * self.grid_size), ((target_y) * self.grid_size), self.grid_size, self.grid_size) not in self.draws:
        self.draws.append((((target_x) * self.grid_size),
          ((target_y) * self.grid_size),
          self.grid_size,
          self.grid_size))
    """

    for draw in self.draws:
      #screen.fill(
      #  self.grid_color,
      #  draw
      #)

      x = Line._grid_object.copy()
      x.fill((self.grid_color))

      if len(self.grid_color) == 4:
        x.set_alpha(self.grid_color[3])

      x = pygame.transform.scale(x, (self.grid_size, self.grid_size))

      screen.blit(
        x, draw[0:2]
      )

  def update(self, screen):
    global mode

    if self.object == None or self.end == None or self.anchor == None:
      return

    render_pos = (min(self.anchor[0], self.end[0]), min(self.anchor[1], self.end[1]))

    screen.blit(self.object, render_pos)

    screen.fill((255, 0, 0), (self.anchor[0]-1, self.anchor[1]-1, 3, 3))

    screen.fill((0, 0, 255), (self.end[0]-1, self.end[1]-1, 3, 3))

    if mode != "vertex edit":
      return

    if mouse_pos[0] <= self.anchor[0] + 5 and mouse_pos[0] >= self.anchor[0] - 5 and mouse_pos[1] <= self.anchor[1] + 5 and mouse_pos[1] >= self.anchor[1] - 5:

      if last_mouse_press[0] == False and mouse_press[0] == True:
        Grab(self, "anchor")

    elif mouse_pos[0] <= self.end[0] + 5 and mouse_pos[0] >= self.end[0] - 5 and mouse_pos[1] <= self.end[1] + 5 and mouse_pos[1] >= self.end[1] - 5:

      if last_mouse_press[0] == False and mouse_press[0] == True:
        Grab(self, "end")

def clear():
  global objects
  for obj in objects:
    obj.delete()

  objects = []

class Polygon:

  _angle_marker = pygame.image.load("./resources/line_color.png")

  def __init__(self, X, Y):
    self.anchor = [X, Y]
    self.vertices = []
    self.grid_color = (0, 0, 0)

    self.transform_history = []

    self.history_seek = -1
    self.rotation = 0
    self.grid_size = _gs
    self.horizontal_scale = 1
    self.verticle_scale = 1
    self.scale = 1
    self.width_scale = 1
    self.height_scale = 1

    self.history_lock = False
    self.selected = False
    self.angle_selected = False
    self.anchor_selected = False
    self.scale_selected = False
    self.height_scale_selected = False
    self.width_scale_selected = False
    self.verticle_scale_selected = False
    self.horizontal_scale_selected = False

    self.type = "Polygon Object"

    self.interface = None

    self.colorview = FunctionTab._x.copy()
    #self.colorview.fill(self.grid_color)
    self.set_color(self.grid_color)

    self.angle_marker = Polygon._angle_marker.copy()
    self.TraceThread = Thread(target=self._threaded_trace)

    #self.TraceThread.start()

    objects.append(self)

    self.add_vertice_from_last(10, 180)

  def extend_config(self, config):
    return config

  @classmethod
  def update_config(cls, config):
    if "horizontal_scale" not in config.keys():
      config.update({"horizontal_scale": 1})
    
    if "verticle_scale" not in config.keys():
      config.update({"verticle_scale": 1})
    
    if "height_scale" not in config.keys():
      config.update({"height_scale": 1})

    if "width_scale" not in config.keys():
      config.update({"width_scale": 1})

    if "grid_color" not in config.keys():
      config.update({"grid_color": (0, 0, 0, 255)})

    if "grid_size" not in config.keys():
      config.update({"grid_size": _gs})


  def save_config(self):
    config = {
      "anchor": self.anchor.copy(),
      "scale": self.scale,
      "horizontal_scale": self.horizontal_scale,
      "verticle_scale": self.verticle_scale,
      "height_scale": self.height_scale,
      "width_scale": self.width_scale,
      "type": self.type,
      "kwargs": {"X": self.anchor[0], "Y": self.anchor[1]},
      "grid_size": self.grid_size,
      "grid_color": list(self.grid_color),
      "rotation": self.rotation,
      "vertices": [
        {
          "anchor": l.anchor.copy(),
          "angle": l.angle,
          "length": l.length,
          "width": l.width
        } for l in self.vertices
      ]
    }
    return self.extend_config(config)

  @classmethod
  def load_config(cls, config):
    #anchor = [float(config["anchor"][0]), float(config["anchor"][1])]
    scale = float(config["scale"])
    horizontal_scale = float(config["horizontal_scale"])
    verticle_scale = float(config["verticle_scale"])
    width_scale = float(config["width_scale"])
    height_scale = float(config["height_scale"])
    _type = str(config["type"])
    kwargs = config["kwargs"]
    grid_size = int(config["grid_size"])
    rotation = float(config["rotation"])
    vertice_configs = config["vertices"]
    grid_color = tuple(config["grid_color"])

    if _type == "Triangle Object":
      new_poly = Triangle(**kwargs)
    elif _type == "Arc Object":
      new_poly = Arc(**kwargs)
    elif _type == "Circle Object":
      new_poly = Circle(**kwargs)
    elif _type == "Rectangle Object":
      new_poly = Rectangle(**kwargs)
    elif _type == "Polygon Object":
      new_poly = Polygon(**kwargs)

    new_poly.set_scale(scale)
    new_poly.verticle_scale = verticle_scale
    new_poly.horizontal_scale = horizontal_scale
    new_poly.height_scale = height_scale
    new_poly.width_scale = width_scale
    new_poly.type = _type
    new_poly.set_grid_size(grid_size)
    new_poly.set_color(grid_color)
    new_poly.rotate_to(rotation)

    vertices = []
    for conf in vertice_configs:
      l = Line(queue=False)
      l.set_anchor(float(conf["anchor"][0]), int(conf["anchor"][1]))
      l.set_length(float(conf["length"]))
      l.set_angle(float(conf["angle"]))
      l.set_grid_size(grid_size)
      l.width = float(conf["width"])
      l.grid_color = grid_color
      vertices.append(l)

    new_poly.vertices = vertices

    return new_poly

  @classmethod
  def load_configs(cls, configs):
    for config in configs:
      cls.load_config(config)

  def name_save(self):
    TextInput(self.anchor[0] + 50, self.anchor[1] + 50, self.save)

  def save(self, filename):
    json.dump(self.save_config(), open(f"./{filename}.json", "w+"))

  def create_interface(self, parent=None):
    new_interface = Interface(self.type)
    self.interface = new_interface

    if parent == None:
      new_interface.function_tabs = [
        FunctionTab(self.name_save, FunctionTab._save),
        FunctionTab(self.remove_interface, FunctionTab._x),
        FunctionTab(self.delete, FunctionTab._trash)
      ]

    anchor_interface = Interface("Anchor", new_interface, None)
    rotate_interface = Interface("Rotate", new_interface, None)
    scale_interface = Interface("Scale", new_interface)
    color_interface = Interface("Color", new_interface, None)
    line_interface = Interface("Lines", new_interface, None)

    anchor_interface.function_tabs = [
      FunctionTab(self.calibrate_anchor, FunctionTab._align),
      FunctionTab(self.get_anchor, "", "display")
    ]

    rotate_interface.function_tabs = [
      FunctionTab(self.rotate_to, "set 0", kwargs={"angle": 0}),
      FunctionTab(self.rotate, FunctionTab._down_arrow, kwargs={"angle": -10}),
      FunctionTab(self.get_rotation, "", "display"),
      FunctionTab(self.rotate, FunctionTab._up_arrow, kwargs={"angle": 10})
    ]

    scale_interface.function_tabs = [
      FunctionTab(self.set_scale, "set 1", kwargs={"scale": 1}),
      FunctionTab(self.decrement_scale, FunctionTab._down_arrow),
      FunctionTab(self.get_scale, "", "display"),
      FunctionTab(self.increment_scale, FunctionTab._up_arrow)
    ]

    verticle_scale_interface = Interface("Verticle", scale_interface, None)
    horizontal_scale_interface = Interface("Horizontal",scale_interface, None)
    height_scale_interface = Interface("Height", scale_interface, None)
    width_scale_interface = Interface("Width", scale_interface, None)

    verticle_scale_interface.function_tabs = [
      FunctionTab(self.set_verticle_scale, "Set 1", kwargs={"verticle_scale": 1}),
      FunctionTab(self.decrement_verticle_scale, FunctionTab._down_arrow),
      FunctionTab(self.get_verticle_scale, "", "display"),
      FunctionTab(self.increment_verticle_scale, FunctionTab._up_arrow)
    ]

    horizontal_scale_interface.function_tabs = [
      FunctionTab(self.set_horizontal_scale, "Set 1", kwargs={"horizontal_scale": 1}),
      FunctionTab(self.decrement_horizontal_scale, FunctionTab._left_arrow),
      FunctionTab(self.get_horizontal_scale, "", "display"),
      FunctionTab(self.increment_horizontal_scale, FunctionTab._right_arrow)
    ]

    height_scale_interface.function_tabs = [
      FunctionTab(self.set_height_scale, "Set 1", kwargs={"height_scale": 1}),
      FunctionTab(self.decrement_height_scale, FunctionTab._down_arrow),
      FunctionTab(self.get_height_scale, "", "display"),
      FunctionTab(self.increment_height_scale, FunctionTab._up_arrow)
    ]

    width_scale_interface.function_tabs = [
      FunctionTab(self.set_width_scale, "Set 1", kwargs={"width_scale": 1}),
      FunctionTab(self.decrement_width_scale, FunctionTab._left_arrow),
      FunctionTab(self.get_width_scale, "", "display"),
      FunctionTab(self.increment_width_scale, FunctionTab._right_arrow)
    ]

    color_interface.function_tabs = [
      FunctionTab(ColorSelector, self.colorview, kwargs={"x": 1000, "y": 1000, "return_to": self.set_color, "initial_color": self.get_color})
    ]

    line_interface.function_tabs = [
      FunctionTab(self.add_vertice_from_last, FunctionTab._add_line_end, kwargs={"length": 20, "angle": 90}),
      FunctionTab(self.add_vertice_from_last, FunctionTab._add_line_start, kwargs={"length": 20, "angle": 90, "index": 0}),
      FunctionTab(self.remove_vertice, FunctionTab._remove_line_end),
      FunctionTab(self.remove_vertice, FunctionTab._remove_line_start, kwargs={"i": 0})
    ]

    self.extended_interface(new_interface)

  def extended_interface(self, interface):
    pass

  def delete(self):
    self.remove_interface()
    objects.remove(self)
    del self

  def get_color(self):
    return self.grid_color

  def remove_interface(self):
    Interface._children.remove(self.interface)
    self.interface = None  

  def snap(self):
    self.move_to(
      ((self.anchor[0]//self.grid_size)*self.grid_size),
      ((self.anchor[1]//self.grid_size)*self.grid_size)
    )

  def calibrate_anchor(self):

    self.add_to_history(
      {
        "Event": "self.calibrate_anchor()",
        "EventValue": None,
        "Inverse": "self.set_anchor(*{})",
        "InverseValue": tuple(self.anchor.copy()),
        "AddValues": False
      }
    )
    sum_x = 0
    sum_y = 0
    l = len(self.vertices) * 2
    for v in self.vertices:
      sum_x += v.anchor[0] + v.end[0]
      sum_y += v.anchor[1] + v.end[1]

    self.anchor = [sum_x/l, sum_y/l]

  def set_scale(self, scale):

    self.add_to_history(
      {
        "Event": "self.set_scale({})",
        "EventValue": scale,
        "Inverse": "self.set_scale({})",
        "InverseValue": self.scale,
        "Flags": ["Replace-Event-Value"]
      }
    )
    
    scale = max(0.1, scale)

    for v in self.vertices:
      prev_anchor = v.anchor.copy()
      prev_end = v.end.copy()

      a_dx = prev_anchor[0] - self.anchor[0]
      a_dy = prev_anchor[1] - self.anchor[1]
      anchor_dist = math.sqrt(
        (a_dx ** 2) +
        (a_dy ** 2)
      )

      e_dx = prev_end[0] - self.anchor[0]
      e_dy = prev_end[1] - self.anchor[1]
      end_dist = math.sqrt(
        (e_dx ** 2) +
        (e_dy ** 2)
      )

      if anchor_dist != 0:
        a_s = math.degrees(math.asin(a_dy/anchor_dist))
        if a_s == 0:
          a_s = 1

        angle_to_anchor = math.degrees(math.acos(a_dx/anchor_dist)) * (a_s/abs(a_s))
      else:
        angle_to_anchor = 0
      
      if end_dist != 0:
        e_s = math.degrees(math.asin(e_dy/end_dist))
        if e_s == 0:
          e_s = 1

        angle_to_end = math.degrees(math.acos(e_dx/end_dist)) * (e_s/abs(e_s))
      else:
        angle_to_end = 0

      scale_dist_a = (anchor_dist / self.scale) * scale
      scale_dist_e = (end_dist / self.scale) * scale

      new_ax = math.cos(math.radians(angle_to_anchor)) * scale_dist_a
      new_ay = math.sin(math.radians(angle_to_anchor)) * scale_dist_a

      new_ex = math.cos(math.radians(angle_to_end)) * scale_dist_e
      new_ey = math.sin(math.radians(angle_to_end)) * scale_dist_e

      v.set_anchor(self.anchor[0] + new_ax, self.anchor[1] + new_ay)
      v.set_end(self.anchor[0] + new_ex, self.anchor[1] + new_ey)

      del new_ax, new_ay, new_ex, new_ey, scale_dist_a, scale_dist_e, angle_to_anchor, angle_to_end, anchor_dist, end_dist

    self.scale = scale

  def decrement_scale(self):
    self.set_scale(round(max(0.1, self.scale - 0.1), 1))

  def increment_scale(self):
    self.set_scale(round(self.scale + 0.1, 1))

  def get_scale(self):
    return self.scale

  def get_rotation(self):
    return self.rotation

  def get_anchor(self):
    return self.anchor

  def set_verticle_scale(self, verticle_scale):

    self.add_to_history(
      {
        "Event": "self.set_verticle_scale({})", 
        "EventValue": verticle_scale,
        "Inverse": "self.set_verticle_scale({})",
        "InverseValue": float(str(self.verticle_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    verticle_scale = max(verticle_scale, 0.1)
    rate = (verticle_scale / self.verticle_scale)
    for v in self.vertices:
      dy = v.anchor[1] - self.anchor[1]
      dy1 = v.end[1] - self.anchor[1]
      dy *= rate
      dy1 *= rate
      v.set_anchor(v.anchor[0], self.anchor[1] + dy)
      v.set_end(v.end[0], self.anchor[1] + dy1)
    self.verticle_scale = verticle_scale

  def set_horizontal_scale(self, horizontal_scale):

    self.add_to_history(
      {
        "Event": "self.set_horizontal_scale({})",
        "EventValue": horizontal_scale,
        "Inverse": "self.set_horizontal_scale({})",
        "InverseValue": float(str(self.horizontal_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    horizontal_scale = max(horizontal_scale, 0.1)
    rate = (horizontal_scale/self.horizontal_scale)
    for v in self.vertices:
      dx = v.anchor[0] - self.anchor[0]
      dx1 = v.end[0] - self.anchor[0]
      dx *= rate
      dx1 *= rate
      v.set_anchor(self.anchor[0] + dx, v.anchor[1])
      v.set_end(self.anchor[0] + dx1, v.end[1])
    self.horizontal_scale = horizontal_scale

  def increment_horizontal_scale(self):
    self.set_horizontal_scale(round(self.horizontal_scale + 0.1, 1))

  def decrement_horizontal_scale(self):
    self.set_horizontal_scale(round(max(self.horizontal_scale - 0.1, 0.1), 1))

  def increment_verticle_scale(self):
    self.set_verticle_scale(round(self.verticle_scale + 0.1, 1))
  
  def decrement_verticle_scale(self):
    self.set_verticle_scale(round(max(self.verticle_scale - 0.1, 0.1), 1))

  def get_verticle_scale(self):
    return self.verticle_scale
  
  def get_horizontal_scale(self):
    return self.horizontal_scale

  def get_height_scale(self):
    return self.height_scale
  
  def get_width_scale(self):
    return self.width_scale

  def set_height_scale(self, height_scale):

    self.add_to_history(
      {
        "Event": "self.set_height_scale({})",
        "EventValue": height_scale,
        "Inverse": "self.set_height_scale({})",
        "InverseValue": float(str(self.height_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    self.history_lock = True
    height_scale = max(height_scale, 0.1)
    r = self.rotation
    rate = (height_scale / self.height_scale)
    self.rotate_to(0)
    for v in self.vertices:
      dy = v.anchor[1] - self.anchor[1]
      dy1 = v.end[1] - self.anchor[1]
      dy *= rate
      dy1 *= rate
      v.set_anchor(v.anchor[0], self.anchor[1] + dy)
      v.set_end(v.end[0], self.anchor[1] + dy1)
    self.height_scale = height_scale
    self.rotate_to(r)
    self.history_lock=False

  def set_width_scale(self, width_scale):

    self.add_to_history(
      {
        "Event": "self.set_width_scale({})",
        "EventValue": width_scale,
        "Inverse": "self.set_width_scale({})",
        "InverseValue": float(str(self.width_scale)),
        "Flags": ["Replace-Event-Value"]
      }
    )
    self.history_lock = True
    width_scale = max(width_scale, 0.1)
    r = self.rotation
    rate = (width_scale/self.width_scale)
    self.rotate_to(0)
    for v in self.vertices:
      dx = v.anchor[0] - self.anchor[0]
      dx1 = v.end[0] - self.anchor[0]
      dx *= rate
      dx1 *= rate
      v.set_anchor(self.anchor[0] + dx, v.anchor[1])
      v.set_end(self.anchor[0] + dx1, v.end[1])
    self.width_scale = width_scale
    self.rotate_to(r)
    self.history_lock = False

  def increment_height_scale(self):
    self.set_height(self.height_scale + 0.1)

  def decrement_height_scale(self):
    self.set_height(max(0.1, self.height - 0.1))

  def increment_width_scale(self):
    self.set_width_scale(self.length + 0.1)

  def decrement_width_scale(self):
    self.set_width_scale(max(0.1, self.length - 0.1))

  def check_select(self, screen):
    minpos = None
    maxpos = None

    if mouse_press[0] == False and last_mouse_press[0] == True:
      self.add_to_history(
        {
          "Event": "# Skip",
          "EventValue": None,
          "Inverse": "# Skip",
          "InverseValue": None,
          "Flags": ["AddValues"]
        }
      )

    if len(self.vertices) == 0:
      return

    for l in self.vertices:
      if minpos == None:
        minpos = [min(l.anchor[0], l.end[0]), min(l.anchor[1], l.end[1])]

      if maxpos == None:
        maxpos = [max(l.anchor[0], l.end[0]), max(l.anchor[1], l.end[1])]
      
      minpos[0] = min(
        min(l.anchor[0], l.end[0]),
        minpos[0]
      )
      minpos[1] = min(
        min(l.anchor[1], l.end[1]),
        minpos[1]
      )
      maxpos[0] = max(
        max(l.anchor[0], l.end[0]),
        maxpos[0]
      )
      maxpos[1] = max(
        max(l.anchor[1], l.end[1]),
        maxpos[1]
      )

    if mouse_press[0] == True and last_mouse_press[0] == False:
      if minpos[0] - 1 <= mouse_pos[0] and maxpos[0] + 1 >= mouse_pos[0] and minpos[1] - 1 <= mouse_pos[1] and maxpos[1] + 1 >= mouse_pos[1]:
        self.selected = True

        if self.interface == None:
          self.create_interface()

      elif self.selected == True:
        self.selected = False

    if self.selected:
      screen.fill(
        (0, 255, 0),
        (minpos[0], minpos[1], maxpos[0] - minpos[0], 1)
      )
      screen.fill(
        (0, 255, 0),
        (minpos[0], minpos[1], 1, maxpos[1] - minpos[1])
      )
      screen.fill(
        (0, 255, 0),
        (maxpos[0], minpos[1], 1, maxpos[1] - minpos[1])
        )
      screen.fill(
        (0, 255, 0),
        (minpos[0], maxpos[1], maxpos[0] - minpos[0], 1)
      )

  def rotate(self, angle):

    self.add_to_history(
      {
        "Event": "self.rotate({})",
        "EventValue": angle,
        "Inverse": "self.rotate({})",
        "InverseValue": -angle,
        "Flags": ["AddValues"]
      }
    )
    anchor = self.anchor.copy()

    self.rotation += angle

    for v in self.vertices:

      dx = v.anchor[0] - anchor[0]
      dy = v.anchor[1] - anchor[1]

      dist = math.sqrt((dx ** 2) + (dy ** 2))

      if dist != 0:
        s = math.degrees(math.asin(dy/dist))
        if s == 0:
          s = 1
        rot = math.degrees(math.acos(dx/dist)) * (s/abs(s))

        rot += angle

        new_x = math.cos(math.radians(rot)) * dist
        new_y = math.sin(math.radians(rot)) * dist

        v.set_anchor(anchor[0] + new_x, anchor[1] + new_y)

      v.set_angle(v.angle + angle)

  def rotate_to(self, angle):
    r = angle - self.rotation
    self.rotate(r)

  def rotate_towards(self, position):
    x, y = position

    dx = x - self.anchor[0]
    dy = y - self.anchor[1]

    dist = math.sqrt((dx ** 2) + (dy ** 2))

    if dist != 0:
      s = math.degrees(math.asin(dy/dist))
      if s == 0:
        s = 1
      rot = math.degrees(math.acos(dx/dist)) * (s/abs(s))

    else:
      rot = 0
    
    self.rotate_to(rot)

  def move(self, x, y):

    self.add_to_history(
      {
        "Event": "self.move(*{})",
        "EventValue": (x, y),
        "Inverse": "self.move(*{})",
        "InverseValue": (-x, -y),
        "Flags": ["AddValues"]
      }
    )
    self.anchor[0] += x
    self.anchor[1] += y

    for v in self.vertices:
      v.set_anchor(v.anchor[0] + x, v.anchor[1] + y)

  def move_to(self, x, y):
    dx = x - self.anchor[0]
    dy = y - self.anchor[1]

    self.move(dx, dy)

  def set_color(self, color):
    self.grid_color = color
    for v in self.vertices:
      v.set_color(color)

    self.colorview.fill(self.grid_color)

  def set_vertices(self, *vertices):

    #self.transform_history.append()
    self.vertices = list(vertices)
    for v in self.vertices:
      v.grid_color = self.grid_color

  def set_anchor(self, X, Y):
    self.add_to_history(
      {
        "Event": "self.set_anchor(*{})",
        "EventValue": (X, Y),
        "Inverse": "self.set_anchor(*{})",
        "InverseValue": tuple(self.anchor),
        "Flags": []
      }
    )
    self.anchor = [X, Y]

  def add_vertice(self, X, Y, index=-1):
    n = Line(queue=False)

    if len(self.vertices) == 0:
      if index < 0:
        n.set_anchor(*tuple(self.anchor))
      else:
        n.set_end(*tuple(self.anchor))

    else:
      if index < 0:
        n.set_anchor(*tuple(self.vertices[len(self.vertices) - 1].end))
      else:
        n.set_end(*tuple(self.vertices[index].end))

    if index < 0:
      n.set_end(X, Y)
    else:
      e = tuple(n.end)
      n.set_anchor(X, Y)
      n.set_end(*e)

    n.set_grid_size(self.grid_size)
    n.grid_color = self.grid_color

    if index < 0:
      self.vertices.append(n)
    
    else:
      self.vertices.insert(index, n)

  def remove_vertice(self, i=-1):
    try:
      self.vertices.remove(self.vertices[i])
    
    except:
      raise Exception(f"No Vertice Found in position {i}")

  def add_vertice_from_last(self, length, angle, relative_angle=True, index=-1):
    n = Line(queue=False)

    if len(self.vertices) == 0:
      n.set_anchor(*tuple(self.anchor))
      n.set_angle(angle)
      n.set_length(length)

    else:

      if index < 0:
        n.set_anchor(*tuple(self.vertices[len(self.vertices) - 1].end))

      else:
        n.set_anchor(*tuple(self.vertices[index].anchor))

      n.set_length(length)

      if relative_angle:
        n.set_angle(
          angle + self.vertices[len(self.vertices) - 1].angle
        )

        if index >= 0:
          n.set_angle(
            angle + self.vertices[index].angle
          )
          e = tuple(n.end)
          a = tuple(n.anchor)
          n.set_anchor(*e)
          n.set_end(*a)

      else:
        n.set_angle(angle)

    n.set_grid_size(self.grid_size)
    n.grid_color = self.grid_color

    if index < 0:
      self.vertices.append(n)

    else:
      self.vertices.insert(index, n)

  def set_grid_size(self, grid_size):
    self.add_to_history(
      {
        "Event": "self.set_grid_size({})",
        "EventValue": grid_size,
        "Inverse": "self.set_grid_size({})",
        "InverseValue": self.grid_size,
        "Flags": ["AddValues"]
      }
    )
    self.grid_size = grid_size
    for v in self.vertices:
      v.set_grid_size(grid_size)

  def add_to_history(self, event_obj):
    if self.history_lock:
      return
    
    if self.history_seek != -1:
      try:
        if self.history_seek < -1:
          x = len(self.transform_history)
          while True:
            self.transform_history.pop(x + self.history_seek)

        else:
          while True:
            self.transform_history.pop(self.history_seek)

      except:
        self.transform_history.append(
          {
            "Event": "# Skip",
            "EventValue": None,
            "Inverse": "# Skip",
            "InverseValue": None,
            "Flags": ["Replace-Event-Value"]
          }
        )

      self.history_seek = -1

    self.history_seek = -1
    if len(self.transform_history) == 0:
      self.transform_history.append(event_obj)

    elif "Replace-Event-Value" in event_obj["Flags"]:
      old = self.transform_history.pop(-1)
      if "Replace-Event-Value" in old["Flags"]:
        if event_obj["Event"] == old["Event"]:
          old["EventValue"] = event_obj["EventValue"]
          self.transform_history.append(old)

        else:
          self.transform_history.append(old)
          self.transform_history.append(event_obj)

      else:
        self.transform_history.append(old)
        self.transform_history.append(event_obj)

    elif "AddValues" in event_obj["Flags"]:
      old = self.transform_history.pop(-1)

      if "AddValues" in old["Flags"]:
        if event_obj["Event"] == old["Event"]:
          old_event_val = old["EventValue"]
          if isinstance(old_event_val, tuple):
            new_val1 = []
            new_val2 = []
            for x in range(len(old_event_val)):
              new_val1.append(old["EventValue"][x] + event_obj["EventValue"][x])
              new_val2.append(old["InverseValue"][x] + event_obj["InverseValue"][x])
            old["EventValue"] = tuple(new_val1)
            old["InverseValue"] = tuple(new_val2)

          elif isinstance(old_event_val, int) or isinstance(old_event_val, float):
            old["EventValue"] += event_obj["EventValue"]
            old["InverseValue"] += event_obj["InverseValue"]

          self.transform_history.append(old)
        
        else:
          self.transform_history.append(old)
          self.transform_history.append(event_obj)


      else:
        self.transform_history.append(old)
        self.transform_history.append(event_obj)

  def history(self):
    return self.transform_history

  def undo(self):
    self.history_lock = True
    if len(self.transform_history) == 0:
      self.history_lock = False
      print("Nothing left to undo")
      return

    event_obj = self.transform_history[self.history_seek]
    while event_obj["Event"] == "# Skip":
      self.transform_history.pop(len(self.transform_history) + self.history_seek)
      event_obj = self.transform_history[self.history_seek]
      if len(self.transform_history) + self.history_seek < 0:
        break

    invert = event_obj["Inverse"]
    #try:
    exec(f"{invert.format(str(event_obj['InverseValue']))}")
    
    #except Exception as e:
    #  print(f"Could not undo:\n{e}")
    #  self.history_lock = False
    #  return

    self.history_seek -= 1
    self.history_lock = False

  def redo(self):
    self.history_lock = True
    if len(self.transform_history) == 0 or self.history_seek == -1 or self.history_seek == len(self.transform_history) - 1:
      self.history_lock = False
      print("Nothing left to redo")
      return

    event_obj = self.transform_history[self.history_seek + 1]

    event = event_obj["Event"]

    try:
      exec(f"{event.format(str(event_obj['EventValue']))}")

    except:
      print("Could not redo")
      self.history_lock = False
      return

    self.history_seek += 1
    self.history_lock = False

  def _single_thread_trace(self):
    unique_draws = []
    for v in self.vertices:
      v._threaded_trace()

      replacement = []
      for draw in v.draws:
        if draw not in unique_draws:
          replacement.append(draw)
        
          unique_draws.append(draw)
      
      v.draws = replacement.copy()

  def _threaded_trace(self):
    global split_trace_threads
    while split_trace_threads:
      unique_draws = []
      for v in self.vertices:
        v._threaded_trace()

        replacement = []
        for draw in v.draws:
          if draw not in unique_draws:
            replacement.append(draw)
          
            unique_draws.append(draw)

  def trace(self, screen):
    for v in self.vertices:
      v.trace(screen)

  def extend_update(self, screen):
    pass

  def update(self, screen):
    global mode
    if self.anchor == None:
      return

    for v in self.vertices:
      v.update(screen)

    # angle
    xp = 30 * math.cos(math.radians(self.rotation))
    yp = 30 * math.sin(math.radians(self.rotation))

    xp += self.anchor[0]
    yp += self.anchor[1]

    screen.fill(
      (255, 255, 0),
      (xp - 1, yp - 1, 3, 3)
    )

    screen.fill(
      (255, 127, 0),
      (self.anchor[0] + ((math.cos(math.radians(45))*self.scale * 10) - 1), (self.anchor[1] - (math.sin(math.radians(45))*self.scale*10)) - 1, 3, 3)
    )

    screen.fill(
      (0, 127, 255),
      (
        (self.anchor[0] + (self.horizontal_scale * 10)) - 1,
        self.anchor[1] - 1, 3, 3
      )
    )

    screen.fill(
      (0, 127, 255),
      (
        self.anchor[0] - 1,
        (self.anchor[1] - (self.verticle_scale * 10)) - 1,
        3, 3
      )
    )

    screen.fill(
      (0, 200, 200),
      (
        (math.cos(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[0] - 1,
        (math.sin(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[1] - 1,
        3, 3
      )
    )

    screen.fill(
      (0, 200, 200),
      (
        (math.cos(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[0] - 1,
        (math.sin(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[1] - 1,
        3, 3
      )
    )

    # Line Manipulators
    if self.selected and mode == "vertex edit":
      screen.blit(
        FunctionTab._add_line_start,
        (
          self.anchor[0] - 45,
          self.anchor[1] - 45
        )
      )
      screen.blit(
        FunctionTab._add_line_end,
        (
          self.anchor[0] - 25,
          self.anchor[1] - 45
        )
      )
      screen.blit(
        FunctionTab._remove_line_start,
        (
          self.anchor[0] - 45,
          self.anchor[1] - 25
        )
      )
      screen.blit(
        FunctionTab._remove_line_end,
        (
          self.anchor[0] - 25,
          self.anchor[1] - 25
        )
      )

    if self.angle_selected:
      self.rotate_towards(mouse_pos)

    if self.anchor_selected:
      self.move_to(mouse_pos[0], mouse_pos[1])

    if self.scale_selected:
      self.set_scale(((mouse_pos[0] - self.anchor[0]) * math.sqrt(2)) / 10)

    if self.horizontal_scale_selected:
      self.set_horizontal_scale((mouse_pos[0] - self.anchor[0])/10)

    if self.verticle_scale_selected:
      self.set_verticle_scale((self.anchor[1] - mouse_pos[1])/10)

    if self.width_scale_selected:
      d = math.sqrt(((mouse_pos[1] - self.anchor[1]) ** 2) + ((mouse_pos[0] - self.anchor[0]) ** 2))
      
      self.set_width_scale(d / 10)

    if self.height_scale_selected:
      d = math.sqrt(((mouse_pos[1] - self.anchor[1]) ** 2) + ((mouse_pos[0] - self.anchor[0]) ** 2))
      
      self.set_height_scale(d / 10)

    if mouse_press[0] == True and last_mouse_press[0] == False and mode == "vertex edit":
      if xp - 2 <= mouse_pos[0] and xp + 2 >= mouse_pos[0] and yp - 2 <= mouse_pos[1] and yp + 2 >= mouse_pos[1]:
        self.angle_selected = True

      elif self.angle_selected:
        self.angle_selected = False

      if self.anchor[0] - 2 <= mouse_pos[0] and self.anchor[0] + 2 >= mouse_pos[0] and self.anchor[1] - 2 <= mouse_pos[1] and self.anchor[1] + 2 >= mouse_pos[1]:
        self.anchor_selected = True

      elif self.anchor_selected:
        self.anchor_selected = False

      # check scale selection
      if (self.anchor[0] + (math.cos(math.radians(45)) * self.scale * 10)) - 2 <= mouse_pos[0] and (self.anchor[0] + (math.cos(math.radians(45)) * self.scale * 10)) + 2 >= mouse_pos[0] and (self.anchor[1] - (math.sin(math.radians(45)) * self.scale * 10)) - 2 <= mouse_pos[1] and (self.anchor[1] - (math.sin(math.radians(45)) * self.scale * 10)) + 2 >= mouse_pos[1]:
        self.scale_selected = True
        self.anchor_selected = False

      elif self.scale_selected:
        self.scale_selected = False

      # check horizontal scale selection
      if (self.anchor[0] + (10 * self.horizontal_scale)) - 2 <= mouse_pos[0] and (self.anchor[0] + (10 * self.horizontal_scale)) + 2 >= mouse_pos[0] and self.anchor[1] - 2 <= mouse_pos[1] and self.anchor[1] + 2 >= mouse_pos[1]:
        self.horizontal_scale_selected = True
        self.anchor_selected = False

      elif self.horizontal_scale_selected:
        self.horizontal_scale_selected = False

      # check verticle scale selection
      if self.anchor[0] - 2 <= mouse_pos[0] and self.anchor[0] + 2 >= mouse_pos[0] and (self.anchor[1] - (10 * self.verticle_scale)) - 2 <= mouse_pos[1] and (self.anchor[1] - (10 * self.verticle_scale)) + 2 >= mouse_pos[1]:
        self.verticle_scale_selected = True
        self.anchor_selected = False

      elif self.verticle_scale_selected:
        self.verticle_scale_selected = False

      # check width scale selection
      if (math.cos(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[0] - 2 <= mouse_pos[0] and (math.cos(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[0] + 2 >= mouse_pos[0] and (math.sin(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[1] - 2 <= mouse_pos[1] and (math.sin(math.radians(self.rotation)) * (self.width_scale * 10)) + self.anchor[1] + 2 >= mouse_pos[1]:
        self.width_scale_selected = True
        self.anchor_selected = False

      elif self.width_scale_selected:
        self.width_scale_selected = False


      # check height scale selection
      if (math.cos(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[0] - 2 <= mouse_pos[0] and (math.cos(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[0] + 2 >= mouse_pos[0] and (math.sin(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[1] - 2 <= mouse_pos[1] and (math.sin(math.radians(self.rotation - 90)) * (self.height_scale * 10)) + self.anchor[1] + 2 >= mouse_pos[1]:
        self.height_scale_selected = True
        self.anchor_selected = False

      elif self.height_scale_selected:
        self.height_scale_selected = False

      if self.selected:
        if self.anchor[0] - 46 <= mouse_pos[0] and self.anchor[0] - 29 >= mouse_pos[0] and self.anchor[1] - 46 <= mouse_pos[1] and self.anchor[1] - 29 >= mouse_pos[1]:
          self.add_vertice_from_last(20, 90, index=0)

        if self.anchor[0] - 26 <= mouse_pos[0] and self.anchor[0] - 9 >= mouse_pos[0] and self.anchor[1] - 46 <= mouse_pos[1] and self.anchor[1] - 29 >= mouse_pos[1]:
          self.add_vertice_from_last(20, 90)

        if self.anchor[0] - 46 <= mouse_pos[0] and self.anchor[0] - 29 >= mouse_pos[0] and self.anchor[1] - 26 <= mouse_pos[1] and self.anchor[1] - 9 >= mouse_pos[1]:
          self.remove_vertice(0)

        if self.anchor[0] - 26 <= mouse_pos[0] and self.anchor[0] - 9 >= mouse_pos[0] and self.anchor[1] - 26 <= mouse_pos[1] and self.anchor[1] - 9 >= mouse_pos[1]:
          self.remove_vertice()

    if mouse_press[0] == False and last_mouse_press[0] == True:
      self.angle_selected = False
      self.anchor_selected = False
      self.scale_selected = False
      self.width_scale_selected = False
      self.height_scale_selected = False
      self.verticle_scale_selected = False
      self.horizontal_scale_selected = False

    # anchor
    screen.fill(
      (255, 0, 255),
      (self.anchor[0] - 1, self.anchor[1] - 1, 3, 3)
    )

    self.extend_update(screen)

class Triangle(Polygon):
  
    def __init__(self, X, Y, radius):
        super().__init__(X, Y)

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

class Rectangle(Polygon):

  def __init__(self, X, Y, length, height, rotation=0):

    super().__init__(X, Y)
    self.type = "Rectangle Object"
    self.rotation = rotation
    self.length = length
    self.height = height
    
    x1 = self.anchor[0]
    y1 = self.anchor[1]

    x1 += math.cos(math.radians(self.rotation)) * (self.length/2)
    y1 += math.sin(math.radians(self.rotation)) * (self.length/2)

    x1 += math.cos(math.radians(self.rotation + 90)) * (self.height/2)
    y1 += math.sin(math.radians(self.rotation + 90)) * (self.height/2)

    self.vertices[0].set_anchor(x1, y1)
    self.vertices[0].set_length(self.length)
    self.vertices[0].set_angle(self.rotation)

    self.add_vertice_from_last(self.height, 90)
    self.add_vertice_from_last(self.length, 90)
    self.add_vertice_from_last(self.height, 90)

  def extended_interface(self, interface):
    interface.type = "Rectangle Object"

  def extend_config(self, config):

    config["type"] = "Rectangle Object"
    config["kwargs"].update(
      {"length": self.length, "height": self.height, "rotation": self.rotation}
    )

    return config

class Arc(Polygon): # Converting to Polygon

  #_angle_marker = pygame.image.load("./line_color.png")

  def __init__(self, X, Y):

    super().__init__(X, Y)

    #objects.append(self)
    self.radius = 20
    #self.anchor = None
    self.angle = 0
    self.curve = 45
    self.type = "Arc Object"
    #self.grid_size = 10
    #self.selected = False
    #self.line_segments = []
    #self.angle_marker = ._angle_marker.copy()
    #self.angle_selected = False
    #self.interface = None
    self.set_curve(45)

  def extended_interface(self, interface):
    interface.set_text(self.type)
    new_interface = interface

    self.interface = new_interface

    angle_interface = Interface("Angle", new_interface, None)
    curve_interface = Interface("Curve", new_interface, None)

    angle_interface.function_tabs = [
      FunctionTab(self.set_angle_0, "set 0"),
      FunctionTab(self.decrement_angle, FunctionTab._down_arrow),
      FunctionTab(self.get_angle, "", "display"),
      FunctionTab(self.increment_angle, FunctionTab._up_arrow)
    ]

    curve_interface.function_tabs = [
      FunctionTab(self.set_curve_0, "set 0"),
      FunctionTab(self.decrement_curve, FunctionTab._down_arrow),
      FunctionTab(self.get_curve, "", "display"),
      FunctionTab(self.increment_curve, FunctionTab._up_arrow)
    ]

  #def build_arc(self):
  #  if self.anchor == None or self.radius == None or self.curve == None:
  #    return

  #  for c in range(self.curve // 4):


  def set_grid_size(self, grid_size):
    for l in self.vertices:
      l.set_grid_size(grid_size)

  def increment_radius(self):
    self.set_radius(self.radius + 10)

  def decrement_radius(self):
    self.set_radius(max(self.radius - 10, 0))

  def set_radius_0(self):
    self.set_radius(0)

  def get_radius(self):
    return self.radius

  def increment_angle(self):
    self.set_angle(self.angle + 10)
  
  def decrement_angle(self):
    self.set_angle(self.angle - 10)

  def set_angle_0(self):
    self.set_angle(0)

  def get_angle(self):
    return self.angle

  def increment_curve(self):
    self.set_curve(self.curve + 10)

  def decrement_curve(self):
    self.set_curve(max(self.curve - 10, 0))

  def set_curve_0(self):
    self.set_curve(0)

  def get_curve(self):
    return self.curve

  def set_radius(self, radius, step=5):
    self.radius = radius

    if self.anchor == None:
      return

    self.vertices = []

    _n = step
    for c in range(self.curve // _n):
      pc_a_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)
      pc_a_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)

      n = Line(queue=False)
      n.set_anchor(pc_a_x, pc_a_y)
      n.set_end(pc_b_x, pc_b_y)
      n.grid_size = self.grid_size

      self.vertices.append(n)

  def set_curve(self, curve, step=5):
    self.curve = curve

    if self.anchor == None:
      return

    self.vertices = []

    _n = step
    for c in range(self.curve // _n):
      pc_a_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_x = self.anchor[0] + (math.cos(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)
      pc_a_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n))
      ) * self.radius)
      pc_b_y = self.anchor[1] + (math.sin(
        math.radians(self.angle + (c*_n) + _n)
      ) * self.radius)

      n = Line(queue=False)
      n.set_anchor(pc_a_x, pc_a_y)
      n.set_end(pc_b_x, pc_b_y)
      n.grid_size = self.grid_size

      self.vertices.append(n)


class Circle(Arc):
  
  def __init__(self, X, Y, radius):

    super().__init__(X, Y)

    #self.set_anchor(x, y)
    self.set_radius(radius)
    self.set_curve(360)

  def extend_config(self, config):

    config["type"] = "Circle Object"
    config["kwargs"].update({"radius": self.radius})

    return config

class Animation:
  _objects = []

  def __init__(self, poly=None, commands=[], loop=True):
    self.commands = commands
    self.poly = poly
    self.iter = enumerate(commands)
    self.loop = loop
    self.running = False
    Animation._objects.append(self)

  def start(self):
    self.running = True

  def stop(self):
    self.running = False

  def step(self):
    try:
      i, run = next(self.iter)
    except StopIteration:
      self.iter = enumerate(self.commands)
      i, run = next(self.iter)
    
    exec(f"self.poly.{run['command']}(**{run['kwargs']})")

  def check_select(self, *args, **kwargs):
    pass

  def _update(self, *args, **kwargs):

    if (not self.running) or (len(self.commands) == 0) or (self.poly == None):
      return

    self.step()

  @classmethod
  def update(cls, *args, **kwargs):
    for obj in cls._objects:
      obj._update()


class mouse_grid:
  
  @staticmethod
  def check_select(*a, **b):
    pass

  @staticmethod
  def update(screen):

    if not show_environment_grid:
      return

    w = screen.get_width()
    h = screen.get_height()

    W = (w//_gs) + 1
    H = (h//_gs) + 1

    for y in range(H):
      screen.fill(
        (100, 100, 100, 127),
        (0, y*_gs, w*_gs, 1)
      )

    for x in range(W):
      screen.fill(
        (100, 100, 100, 127),
        (x*_gs, 0, 1, h*_gs)
      )

ui.append(mouse_grid)

rotate_anim = Animation(
  commands = [{"command": "rotate", "kwargs": {"angle": 5}}]
)

def animate(poly: Polygon, anim:str="rotate"):
  if anim == "rotate":
    return Animation(
      poly = poly,
      commands = [
        {
          "command": "rotate",
          "kwargs": {
            "angle": 5
          }
        }
      ]
    )
  
  elif anim == "scale":
    c = {
      "command": "increment_scale",
      "kwargs": {}
    }
    c1 = {
      "command": "decrement_scale",
      "kwargs": {}
    }
    return Animation(
      poly = poly,
      commands = [
        c, c, c, c, c, c, c, c, c, c, c, c, c, c, c,
        c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1, c1,
        c1, c1, c1, c1, c1, c1, c1, c1, c1,
        c, c, c, c, c, c, c, c, c, c
      ]
    )

ui.append(Animation)

def set_mode(m):
  global mode
  mode = m

show_line = True
show_grid = False
show_environment_grid = True
running = True
def InputLoop():
  global running, show_line, mode
  while running:
    user_in = input("enter cmd > ")
    if user_in == "":
      continue
    try:
      exec(
        f"""n = {user_in}\nif n != None:\n  print(n)"""
        )
    except Exception as e:
      print(e)

def to_image(objs, name):
  raw_data = []
  for obj in objs:
    if isinstance(obj, Line):
      if len(obj.draws) == 0:
        raise ValueError("object fill hasn't been activated")
      for d in obj.draws:
        raw_data.append((d, obj.grid_color))
    
    else:
      for v in obj.vertices:
        if len(v.draws) == 0:
          raise ValueError("object fill hasn't been activated")
        for d in v.draws:
          raw_data.append((d, obj.grid_color))

  min_x = 1000
  min_y = 1000
  max_x = 0
  max_y = 0
  for t in raw_data:
    pos, col = t
    x, y, w, h = pos

    x = x//_gs
    y = y//_gs
    
    min_x = min(x, min_x)
    min_y = min(y, min_y)
    max_x = max(x, max_x)
    max_y = max(y, max_y)

  width = int(max_x - min_x) + 1
  height = int(max_y - min_y) + 1

  data = [[(0, 0, 0, 0) for j in range(width)] for i in range(height)]

  for t in raw_data:
    pos, col = t
    x, y, w, h = pos
    x = x//_gs
    y = y//_gs

    x -= min_x
    y -= min_y

    x = int(x)
    y = int(y)
    if len(col) == 3:
      r, g, b = col
      data[y][x] = (r, g, b, 255)

    elif len(col) == 4:
      r, g, b, a = col
      data[y][x] = (r, g, b, a)

  dat = []
  for l in data:
    for _l in l:
      dat.append(_l)

  img = Image.new("RGBA", (width, height))
  img.putdata(dat)
  img.save(f"{name}.png")


def get(i=0):
  return objects[i]

def hide_lines():
  global show_line
  show_line = False

def show_lines():
  global show_line
  show_line = True

def show_grids():
  global show_grid
  show_grid = True

def hide_grids():
  global show_grid
  show_grid = False

def show_env_grids():
  global show_environment_grid
  show_environment_grid = True

def hide_env_grids():
  global show_environment_grid
  show_environment_grid = False

def get_mode():
  return mode

main_interface = Interface("Environment")

mode_interface = Interface("Mode", main_interface, expanded=None)

mode_interface.function_tabs = [
  FunctionTab(get_mode, "", "display"),
  FunctionTab(set_mode, "[Selection]", kwargs={"m": "selection"}),
  FunctionTab(set_mode, "[Vertex Edit]", kwargs={"m": "vertex edit"})
]

gs = Interface("Grid Size", main_interface, expanded=None)
gsdown = FunctionTab(gs_down, FunctionTab._down_arrow)
gsdisp = FunctionTab(gs_disp, "", "display")
gsup = FunctionTab(gs_up, FunctionTab._up_arrow)

gs.function_tabs = [gsdown, gsdisp, gsup]

_env_grids = Interface("Grid", main_interface, expanded=None)
_env_grids.function_tabs = [
  FunctionTab(hide_env_grids, FunctionTab._visible, "toggle", func2=show_env_grids, surface2=FunctionTab._invisible)
]
_grids = Interface("Fill", main_interface, expanded=None)
_grids.function_tabs = [
  FunctionTab(show_grids, FunctionTab._invisible, "toggle", func2=hide_grids, surface2=FunctionTab._visible)
]
_lines = Interface("Lines", main_interface, expanded=None)
_lines.function_tabs = [
  FunctionTab(hide_lines, FunctionTab._visible, "toggle", func2=show_lines, surface2=FunctionTab._invisible)
]

def place_polygon():
  Polygon(mouse_pos[0], mouse_pos[1])

def place_line():
  l = Line()
  l.set_anchor(mouse_pos[0], mouse_pos[1])

def place_rectangle():
  Rectangle(mouse_pos[0], mouse_pos[1], 100, 100)

def place_triangle():
  Triangle(mouse_pos[0], mouse_pos[1], 50)

def place_arc():
  Arc(mouse_pos[0], mouse_pos[1])

def place_circle():
  Circle(mouse_pos[0], mouse_pos[1], 100)

create_interface = Interface("Create", main_interface, expanded=None)

create_interface.function_tabs = [
  FunctionTab(Place, FunctionTab._polygon, kwargs={"obj": place_polygon}),
  FunctionTab(Place, FunctionTab._rectangle, kwargs={"obj": place_rectangle}),
  FunctionTab(Place, FunctionTab._triangle, kwargs={"obj": place_triangle}),
  FunctionTab(Place, FunctionTab._circle, kwargs={"obj": place_circle}),
  FunctionTab(Place, FunctionTab._arc, kwargs={"obj": place_arc}),
  FunctionTab(Place, FunctionTab._line, kwargs={"obj": place_line})
]

def load_pattern(identifier):

  p = os.scandir()
  names = [n.name for n in p]

  possible_configs = []
  for n in names:
    if n.endswith(".json"):
      possible_configs.append(n)

  results = []
  for n in possible_configs:
    if identifier in n:
      results.append(n)

  if len(results) == 1:
    Polygon.load_config(json.load(open(f"./{results[0]}")))
  
  elif len(results) == 0:
    raise Exception("No Pattern could be found")
  
  else:
    Polygon.load_configs([json.load(open(f"./{n}")) for n in results])
    #raise Exception(f"Multiple Patterns match identifier '{identifier}': {results}")

#poly = Rectangle(336, 142, 100, 100, 25)

split_trace_threads = False
def TraceLoop():
  global split_trace_threads, show_grid
  while not split_trace_threads:
    while show_grid:
      for obj in objects:
        obj._single_thread_trace()

      if split_trace_threads:
        break

TraceThread = Thread(target=TraceLoop)
TraceThread.start()

def single_thread_tracers():
  global split_trace_threads

  if split_trace_threads:
    split_trace_threads = False
    # setting to false should causes TraceThread to stop

    for obj in objects:
      obj.TraceThread.start()

def multi_thread_tracers():
  global split_trace_threads

  if not split_trace_threads:
    split_trace_threads = True
    # setting to true should cause all polygon threads to stop
    TraceThread.start()

InputThread = Thread(target=InputLoop)
InputThread.start()


while running:
  Screen.fill((127, 127, 127))

  mouse_press = list(pygame.mouse.get_pressed())
  mouse_pos = pygame.mouse.get_pos()

  events = []
  for event in pygame.event.get():
    events.append(event)

  for obj in ui:
    obj.check_select(Screen)
    obj.update(Screen)

  if show_grid:
    for obj in objects:
      obj.trace(Screen)

  if show_line:
    Grab.update()
    for obj in objects:
      obj.update(Screen)


  for obj in objects:
    obj.check_select(Screen)

  Interface.update(Screen)

  ColorSelector.check_select(Screen)
  ColorSelector.update(Screen)

  TextInput.check_select(Screen)
  TextInput.update(Screen)

  if mouse_press != last_mouse_press:
    last_mouse_press = mouse_press

  pygame.display.update()
