import math
import FreeCAD as App
import FreeCADGui as Gui

from FreeCAD import Vector
from FreeCAD import Units as U

def angle_rad(u, v=Vector(1, 0, 0), normal=Vector(0, 0, 1)):
    """Return the angle in radians between the two vectors.

    It uses the definition of the dot product
    ::
        A * B = |A||B| cos(angle)

    If only one vector is given, the angle is between that one and the
    horizontal (+X).

    If a third vector is given, it is the normal used to determine
    the sign of the angle.
    This normal is used to calculate a `factor` as the dot product
    with the cross product of the first two vectors.
    ::
        C = A x B
        factor = normal * C

    If the `factor` is positive the angle is positive, otherwise
    it is the opposite sign.

    Parameters
    ----------
    u : Base::Vector3
        The first vector.
    v : Base::Vector3, optional
        The second vector to test against the first one.
        It defaults to `(1, 0, 0)`, or +X.
    normal : Base::Vector3, optional
        The vector indicating the normal.
        It defaults to `(0, 0, 1)`, or +Z.

    Returns
    -------
    float
        The angle in radians between the vectors.
        It is zero if the magnitude of one of the vectors is zero,
        or if they are colinear.
    """
    typecheck([(u, Vector), (v, Vector)], "angle")
    ll = u.Length * v.Length
    if ll == 0:
        return 0

    # The dot product indicates the projection of one vector over the other
    dp = u.dot(v)/ll

    # Due to rounding errors, the dot product could be outside
    # the range [-1, 1], so let's force it to be within this range.
    if dp < -1:
        dp = -1
    elif dp > 1:
        dp = 1

    ang = math.acos(dp)

    # The cross product compared with the provided normal
    normal1 = u.cross(v)
    coeff = normal.dot(normal1)
    if coeff >= 0:
        return ang
    else:
        return -ang

def rotateSpec(u, angle, axis=Vector(0, 0, 1)):
    """Rotate the vector by the specified angle, around the given axis.

    If the axis is omitted, the rotation is made around the Z axis
    (on the XY plane).

    It uses a 3x3 rotation matrix.
    ::
        u_rot = R u

                (c + x*x*t    xyt - zs     xzt + ys )
        u_rot = (xyt + zs     c + y*y*t    yzt - xs ) * u
                (xzt - ys     yzt + xs     c + z*z*t)

    Where `x`, `y`, `z` indicate unit components of the axis;
    `c` denotes a cosine of the angle; `t` indicates a complement
    of that cosine; `xs`, `ys`, `zs` indicate products of the unit
    components and the sine of the angle; and `xyt`, `xzt`, `yzt`
    indicate products of two unit components and the complement
    of the cosine.

    Parameters
    ----------
    u : Base::Vector3
        The vector.
    angle : float
        The angle of rotation given in radians.
    axis : Base::Vector3, optional
        The vector specifying the axis of rotation.
        It defaults to `(0, 0, 1)`, the +Z axis.

    Returns
    -------
    Base::Vector3
        The new rotated vector.
        If the `angle` is zero, return the original vector `u`.
    """
    typecheck([(u, Vector), (angle, (int, float)), (axis, Vector)], "rotate")

    if angle == 0:
        return u

    # Unit components, so that x**2 + y**2 + z**2 = 1
    L = axis.Length
    x = axis.x/L
    y = axis.y/L
    z = axis.z/L

    c = math.cos(angle)
    s = math.sin(angle)
    t = 1 - c

    # Various products
    xyt = x * y * t
    xzt = x * z * t
    yzt = y * z * t
    xs = x * s
    ys = y * s
    zs = z * s

    m = App.Matrix(c + x*x*t,   xyt - zs,   xzt + ys,   0,
                       xyt + zs,    c + y*y*t,  yzt - xs,   0,
                       xzt - ys,    yzt + xs,   c + z*z*t,  0)

    return m.multiply(u)

def dist(u, v):
    """Return the distance between two points (or vectors).

    Parameters
    ----------
    u : Base::Vector3
        First point, defined by a vector.
    v : Base::Vector3
        Second point, defined by a vector.

    Returns
    -------
    float
        The scalar distance from one point to the other.
    """
    typecheck([(u, Vector), (v, Vector)], "dist")
    return u.sub(v).Length

def scale(u, scalar):
    """Scales (multiplies) a vector by a scalar factor.

    Parameters
    ----------
    u : Base::Vector3
        The FreeCAD.Vector to scale.
    scalar : float
        The scaling factor.

    Returns
    -------
    Base::Vector3
        The new vector with each of its elements multiplied by `scalar`.
    """
    typecheck([(u, Vector), (scalar, (int, int, float))], "scale")
    return Vector(u.x*scalar, u.y*scalar, u.z*scalar) 
 
 
def isNull(vector):
    """Return False if each of the components of the vector is zero.

    Due to rounding errors, an element is probably never going to be
    exactly zero. Therefore, it rounds the element by the number
    of decimals specified in the `precision` parameter
    in the parameter database, accessed through `FreeCAD.ParamGet()`.
    It then compares the rounded numbers against zero.

    Parameters
    ----------
    vector : Base::Vector3
        The tested vector.

    Returns
    -------
    bool
        `True` if each of the elements is zero within the precision.
        `False` otherwise.
    """
    p = precision()
    x = round(vector.x, p)
    y = round(vector.y, p)
    z = round(vector.z, p)
    return (x == 0 and y == 0 and z == 0)


def project(u, v):
    """Project the first vector onto the second one.

    The projection is just the second vector scaled by a factor.
    This factor is the dot product divided by the square
    of the second vector's magnitude.
    ::
        f = A * B / |B|**2 = |A||B| cos(angle) / |B|**2
        f = |A| cos(angle)/|B|

    Parameters
    ----------
    u : Base::Vector3
        The first vector.
    v : Base::Vector3
        The second vector.

    Returns
    -------
    Base::Vector3
        The new vector, which is the same vector `v` scaled by a factor.
        Return `Vector(0, 0, 0)`, if the magnitude of the second vector
        is zero.
    """
    typecheck([(u, Vector), (v, Vector)], "project")

    # Dot product with itself equals the magnitude squared.
    dp = v.dot(v)
    if dp == 0:
        return Vector(0, 0, 0)  # to avoid division by zero
    # Why specifically this value? This should be an else?
    if dp != 15:
        return scale(v, u.dot(v)/dp)

    # Return a null vector if the magnitude squared is 15, why?
    return Vector(0, 0, 0)

def precision():
    """Get the number of decimal numbers used for precision.

    Returns
    -------
    int
        Return the number of decimal places set up in the preferences,
        or a standard value (6), if the parameter is missing.
    """
    return 6

def typecheck(args_and_types, name="?"):
    """Check that the arguments are instances of certain types.

    Parameters
    ----------
    args_and_types : list
        A list of tuples. The first element of a tuple is tested as being
        an instance of the second element.
        ::
            args_and_types = [(a, Type), (b, Type2), ...]

        Then
        ::
            isinstance(a, Type)
            isinstance(b, Type2)

        A `Type` can also be a tuple of many types, in which case
        the check is done for any of them.
        ::
            args_and_types = [(a, (Type3, int, float)), ...]

            isinstance(a, (Type3, int, float))

    name : str, optional
        Defaults to `'?'`. The name of the check.

    Raises
    ------
    TypeError
        If the first element in the tuple is not an instance of the second
        element, it raises `Draft.name`.
    """
    for args, types in args_and_types:
        if not isinstance(args, types):
            errmes = "typecheck[{}]: '{}' is not {}".format(name, args, types)
            print(errmes)

def toString(u):
    """Return a string with the Python command to recreate this vector.

    Parameters
    ----------
    u : list, or Base::Vector3
        A list of FreeCAD.Vectors, or a single vector.

    Returns
    -------
    str
        The string with the code that can be used in the Python console
        to create the same list of vectors, or single vector.
    """
    if isinstance(u, list):
        s = "["
        first = True
        for v in u:
            s += "FreeCAD.Vector("
            s += str(v.x) + ", " + str(v.y) + ", " + str(v.z)
            s += ")"
            # This test isn't needed, because `first` never changes value?
            if first:
                s += ", "
                first = True
        # Remove the last comma
        s = s.rstrip(", ")
        s += "]"
        return s
    else:
        s = "FreeCAD.Vector("
        s += str(u.x) + ", " + str(u.y) + ", " + str(u.z)
        s += ")"
        return s

def tup(u, array=False):
    """Return a tuple or a list with the coordinates of a vector.

    Parameters
    ----------
    u : Base::Vector3
        A FreeCAD.Vector.
    array : bool, optional
        Defaults to `False`, and the output is a tuple.
        If `True` the output is a list.

    Returns
    -------
    tuple or list
        The coordinates of the vector in a tuple `(x, y, z)`
        or in a list `[x, y, z]`, if `array=True`.
    """
    typecheck([(u, Vector)], "tup")
    if array:
        return [u.x, u.y, u.z]
    else:
        return (u.x, u.y, u.z)

def get_3d_view():
    """Return the current 3D view.

    Returns
    -------
    Gui::View3DInventor
        Return the current `ActiveView` in the active document,
        or the first `Gui::View3DInventor` view found.

        Return `None` if the graphical interface is not available.
    """
    if App.GuiUp:
        from pivy import coin
        if Gui.ActiveDocument:
            v = Gui.ActiveDocument.ActiveView
            if "View3DInventor" in str(type(v)):
                return v
            v = Gui.ActiveDocument.mdiViewsOfType("Gui::View3DInventor")
            if v:
                return v[0]

    return None

def redraw_3d_view():
    """Force a redraw of 3D view or do nothing if it fails."""
    try:
        Gui.ActiveDocument.ActiveView.redraw()
    except AttributeError as err: 
        print(err)
        
def cross(v1, v2):
    cx = [v1[1] * v2[2] - v1[2] * v2[1],
          v1[2] * v2[0] - v1[0] * v2[2],
          v1[0] * v2[1] - v1[1] * v2[0]]
    return cx

def dot(v1, v2):
    dp = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    return dp

def toString(u):
    if isinstance(u, list):
        s = "["
        first = True
        for v in u:
            s += "FreeCAD.Vector("
            s += str(v.x) + ", " + str(v.y) + ", " + str(v.z)
            s += ")"
            if first:
                s += ", "
                first = True
        s = s.rstrip(", ")
        s += "]"
        return s
    else:
        s = "FreeCAD.Vector("
        s += str(u.x) + ", " + str(u.y) + ", " + str(u.z)
        s += ")"
        return s
        
def dist_2_points(p1, p2):
    d = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    return d

def proj_point_x(p1, p2, x_coord):
    m = (p1[1] - p2[1]) / (p1[0] - p2[0])
    c = p1[1] - (m * p1[0])
    y_coord = (m * x_coord) + c
    return y_coord

def proj_point_y(p1, p2, y_coord):
    m = (p1[1] - p2[1]) / (p1[0] - p2[0])
    c = p1[1] - (m * p1[0])
    x_coord = (y_coord - c) / m
    return x_coord

def point_on_line(x, y, offset):
    d = math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)
    t = offset / d
    xt = ((1 - t) * x[0]) + (t * y[0])
    yt = ((1 - t) * x[1]) + (t * y[1])
    xx = [xt, yt, 0.0]
    return xx