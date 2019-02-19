import numpy as np
import math
from scipy.linalg import expm3

"""
Set of linear algebra and some basic math functions.

Author: Maria Kalemanov (Max Planck Institute for Biochemistry)
"""

__author__ = 'kalemanov'


def perpendicular_vector(iv):
    """
    Finds a unit vector perpendicular to a given vector.
    Implementation of algorithm of Ahmed Fasih https://math.stackexchange.com/
    questions/133177/finding-a-unit-vector-perpendicular-to-another-vector

    Args:
        iv (numpy.ndarray): input 3D vector

    Returns:
        3D vector perpendicular to the input vector (np.ndarray)
    """
    try:
        assert(isinstance(iv, np.ndarray) and iv.shape == (3,))
    except AssertionError:
        print("Requires a 1D numpy.ndarray of length 3 (3D vector)")
        return None
    if iv[0] == iv[1] == iv[2] == 0:
        print("Requires a non-zero 3D vector")
        return None
    ov = np.array([0.0, 0.0, 0.0])
    m = 0
    for m in range(3):
        if iv[m] != 0:
            break
    if m == 2:
        n = 0
    else:
        n = m + 1
    ov[n] = iv[m]
    ov[m] = -iv[n]
    len_outv = math.sqrt(np.dot(ov, ov))
    if len_outv == 0:
        print("Resulting vector has length 0")
        print("given vector: ({}, {}, {})".format(iv[0], iv[1], iv[2]))
        print("resulting vector: ({}, {}, {})".format(ov[0], ov[1], ov[2]))
        return None
    return ov / len_outv  # unit length vector


def rotation_matrix(axis, theta):
    """
    Generates a rotation matrix for rotating a 3D vector around an axis by an
    angle. From B. M. https://stackoverflow.com/questions/6802577/
    python-rotation-of-3d-vector

    Args:
        axis (numpy.ndarray): rotational axis (3D vector)
        theta (float): rotational angle (radians)

    Returns:
        3 x 3 rotation matrix
    """
    a = axis / math.sqrt(np.dot(axis, axis))  # unit vector along axis
    A = np.cross(np.eye(3), a)  # skew-symmetric matrix associated to a
    return expm3(A * theta)


def rotate_vector(v, theta, axis=None, matrix=None, debug=False):
    """
    Rotates a 3D vector around an axis by an angle (wrapper function for
    rotation_matrix).

    Args:
        v (numpy.ndarray): input 3D vector
        theta (float): rotational angle (radians)
        axis (numpy.ndarray): rotational axis (3D vector)
        matrix (numpy.ndarray): 3 x 3 rotation matrix
        debug (boolean): if True (default False), an assertion is done to assure
            that the angle is correct

    Returns:
        rotated 3D vector (numpy.ndarray)
    """
    sqrt = math.sqrt
    dot = np.dot
    acos = math.acos
    pi = math.pi

    if matrix is None and axis is not None:
        R = rotation_matrix(axis, theta)
    elif matrix is not None and axis is None:
        R = matrix
    else:
        print("Either the rotation axis or rotation matrix must be given")
        return None

    u = dot(R, v)
    if debug:
        cos_theta = dot(v, u) / sqrt(dot(v, v)) / sqrt(dot(u, u))
        try:
            theta2 = acos(cos_theta)
        except ValueError:
            if cos_theta > 1:
                cos_theta = 1.0
            elif cos_theta < 0:
                cos_theta = 0.0
            theta2 = acos(cos_theta)
        try:
            assert theta - (0.05 * pi) <= theta2 <= theta + (0.05 * pi)
        except AssertionError:
            print("Angle between the input vector and the rotated one is not "
                  "{}, but {}".format(theta, theta2))
            return None
    return u


def signum(number):
    """
    Returns the signum of a number.

    Args:
        number: a number

    Returns:
        -1 if the number is negative, 1 if it is positive, 0 if it is 0
    """
    if number < 0:
        return -1
    elif number > 0:
        return 1
    else:
        return 0


def dot_norm(p, pnorm, norm):
    """
    Makes the dot-product between the input point and the closest point normal.
    Both vectors are first normalized.

    Args:
        p (numpy.ndarray): the input point, must be float numpy array
        pnorm (numpy.ndarray): the point normal, must be float numpy array
        norm (numpy.ndarray): the closest point normal, must be float numpy
            array

    Returns:
        the dot-product between the input point and the closest point normal
        (float)
    """
    # Point and vector coordinates
    v = pnorm - p

    # Normalization
    mv = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if mv > 0:
        v /= mv
    else:
        return 0
    mnorm = math.sqrt(norm[0]*norm[0] + norm[1]*norm[1] + norm[2]*norm[2])
    if mnorm > 0:
        norm /= mnorm
    else:
        return 0

    return v[0]*norm[0] + v[1]*norm[1] + v[2]*norm[2]