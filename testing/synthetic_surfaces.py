import vtk
from pysurf_compact import pysurf_io as io

"""A set of functions and classes for generating artificial surfaces of
geometrical objects."""


def remove_non_triangle_cells(surface):
    """
    Removes non-triangle cells( e.g. lines and vertices) from the given surface.

    Args:
        surface (vtk.vtkPolyData): a surface

    Returns:
        cleaned surface with only triangular cells (vtk.vtkPolyData)
    """
    print('{} cells including non-triangles'.format(surface.GetNumberOfCells()))
    for i in range(surface.GetNumberOfCells()):
        # Get the cell i and remove if if it's not a triangle:
        cell = surface.GetCell(i)
        if not isinstance(cell, vtk.vtkTriangle):
            surface.DeleteCell(i)
    surface.RemoveDeletedCells()
    print('{} cells after deleting non-triangle cells'.format(
        surface.GetNumberOfCells()))
    return surface


class SphereGenerator(object):
    """
    A class for generating triangular-mesh surface of a sphere.
    """
    @staticmethod
    def generate_sphere_surface(radius=10.0, latitude_res=100,
                                longitude_res=100):
        """
        Generates a sphere surface with only triangular cells.

        Args:
            radius (float, optional): sphere radius (default 10.0)
            latitude_res (int, optional): latitude resolution (default 100)
            longitude_res  (int, optional): latitude resolution (default 100)

        Returns:
            a sphere surface (vtk.vtkPolyData)
        """
        print("Generating a sphere with radius={}, latitude resolution={} and "
              "longitude resolution={}".format(radius, latitude_res,
                                               longitude_res))
        # TODO write a function asserting that an argument is a positive number
        # (int / float) and throw an InputError if it is not
        if not (isinstance(radius, int) or isinstance(radius, float)):
            print "Type error: radius has to be an integer or a float number."
            exit(0)
        if radius <= 0:
            print "Input error: radius has to be positive."
            exit(0)
        sphere = vtk.vtkSuperquadricSource()
        # the origin around which the superquadric should be centered
        sphere.SetCenter(0.0, 0.0, 0.0)
        # allow the superquadric to be scaled in x, y, and z
        sphere.SetScale(1.0, 1.0, 1.0)
        # polygonal discretization in latitude direction
        sphere.SetPhiResolution(latitude_res)
        # polygonal discretization in longitude direction
        sphere.SetThetaResolution(longitude_res)
        # controls size of the superquadric (radius)
        sphere.SetSize(radius)
        # boolean, controls whether a toroidal superquadric is produced
        # (if 0. a sphere is produced)
        sphere.SetToroidal(0)

        # The quadric is made of strips, so pass it through a triangle filter
        # to get a PolyData
        tri = vtk.vtkTriangleFilter()
        tri.SetInputConnection(sphere.GetOutputPort())

        # The quadric has nasty discontinuities from the way the edges are
        # generated, so pass it though a CleanPolyDataFilter to merge any
        # points which are coincident or very close
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputConnection(tri.GetOutputPort())
        cleaner.SetTolerance(0.005)
        cleaner.Update()

        sphere_surface = remove_non_triangle_cells(cleaner.GetOutput())
        return sphere_surface


class CylinderGenerator(object):
    """
    A class for generating triangular-mesh surface of a cylinder.
    """
    @staticmethod
    def generate_cylinder_surface(radius=10.0, height=20.0, res=100):
        """
        Generates a cylinder surface with only triangular cells.

        Args:
            radius (float, optional): cylinder radius (default 10.0)
            height (float, optional): cylinder high (default 20.0)
            res (int, optional): resolution (default 100)

        Returns:
            a cylinder surface (vtk.vtkPolyData)
        """
        print("Generating a cylinder with radius={}, height={} and "
              "resolution={}".format(radius, height, res))
        # TODO write a function asserting that an argument is a positive number
        # (int / float) and throw an InputError if it is not
        if not (isinstance(radius, int) or isinstance(radius, float)):
            print "Type error: radius has to be an integer or a float number."
            exit(0)
        if radius <= 0:
            print "Input error: radius has to be positive."
            exit(0)
        # TODO the same test for high
        cylinder = vtk.vtkCylinderSource()
        # the origin around which the cylinder should be centered
        cylinder.SetCenter(0, 0, 0)
        # the radius of the cylinder
        cylinder.SetRadius(radius)
        # the high of the cylinder
        cylinder.SetHeight(height)
        # polygonal discretization
        cylinder.SetResolution(res)

        # The cylinder is made of strips, so pass it through a triangle filter
        # to get a PolyData
        tri = vtk.vtkTriangleFilter()
        tri.SetInputConnection(cylinder.GetOutputPort())

        # The cylinder has nasty discontinuities from the way the edges are
        # generated, so pass it though a CleanPolyDataFilter to merge any
        # points which are coincident or very close
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputConnection(tri.GetOutputPort())
        cleaner.SetTolerance(0.005)
        cleaner.Update()

        cylinder_surface = remove_non_triangle_cells(cleaner.GetOutput())
        return cylinder_surface


def main():
    """
    Main function generating some sphere and cylinder surfaces.

    Returns:
        None
    """
    fold = "/fs/pool/pool-ruben/Maria/curvature/synthetic_surfaces/"

    # Sphere
    # sg = SphereGenerator()
    # sphere_r1 = sg.generate_sphere_surface(radius=1, latitude_res=10,
    #                                        longitude_res=10)
    # io.save_vtp(sphere_r1, fold + "sphere_r1_res10.vtp")
    #
    # sphere_r5 = sg.generate_sphere_surface(radius=5, latitude_res=50,
    #                                        longitude_res=50)
    # io.save_vtp(sphere_r5, fold + "sphere_r5_res50.vtp")
    #
    # sphere_r10 = sg.generate_sphere_surface()
    # io.save_vtp(sphere_r10, fold + "sphere_r10_res100.vtp")

    # Cylinder
    cg = CylinderGenerator()
    cylinder_r10_h20 = cg.generate_cylinder_surface(res=50)
    io.save_vtp(cylinder_r10_h20, fold + "cylinder_r10_h20_res50.vtp")


if __name__ == "__main__":
    main()