# Usage Guide:
Drop down menu should be self-explanatory

menu can scroll if it goes off screen

# Menus:
\[> Object\]<br>
\[value\] \[modifiers/value displays\]

\[> value group\] \[mods/disps\]<br>
\[sub-value\] \[mods/disps\]

click arrows to collapse/open areas

# Function Symbols:
Trash Can
<ul>
  <li>delete geometry object</li>
</ul>
X
<ul>
  <li>
    remove menu part (object is not
    deleted, and menu can be opened be
    re-selecting the object)
  </li>
</ul>
Save icon
<ul>
  <li>
    saves a shapes values to a json file
    that you name (opens a very simple text box)
  </li>
</ul>

# Geometry Interaction:

mode needs to be set to "vertex edit" in order to modify shapes

Drag Tabs:
<ul>
  <li>Magenta:    Movement</li>
  <li>Yellow:     Rotation</li>
  <li>Orange:     Scale</li>
  <li>Light blue: width/height scale</li>
  <li>Dark blue:  verticle/horizontal scale</li>
</ul>

# Console Commands:
to_image(\<polys\>)
<ul>
  <li>make an image from a list of geometry objects.</li>
  <li>Using `objects` as <polys> will use all
                      objects that are on screen</li>
</ul>

clear()
<ul><li>Deletes all objects</li></ul>
get(<index>)         Returns a geometry object


# Interaction Classes:
<ul>
Polygon                      Base class for all geometry
Triangle (Polygon)
Rectangle (Polygon)
Arc (Polygon)
Circle (Arc)
Line                         Not really meant for direct usage
Animation                    Pretty Complicated, Explained later

Internal Classes: (leave thes alone)
mouse_grid
TextInput
ColorSelector
FunctionTab
Interface
Place
Grab

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

# Triangle Usage:
# Triangle()
#

# Rectangle Usage:
# Rectangle(X, Y, width, height, rotation)

# Arc Usage:
# Arc(X, Y)
#
# Methods:
# .set_curve(a, s)             Regeneratess lines, goes around `a`
#                               degrees in `s` steps.
#                              With (360, 360//x) as args,
#                               generates shape with x sides
#                               (although doesn't always connect
#                               back to start properly)

# Circle Usage:
# Circle(X, Y, radius)