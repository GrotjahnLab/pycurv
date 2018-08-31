from scipy import ndimage
import numpy as np
import vtk
import time

import pexceptions
import pysurf_io as io

"""
Set of functions for running single-layer, signed surface generation from a
membrane segmentation, preprocessing the segmentation and postprocessing the
surface.

Author: Maria Kalemanov (Max Planck Institute for Biochemistry)
"""

__author__ = 'kalemanov'


# when convoluting a binary mask with a gaussian kernel with sigma 1, values 1
# at the boundary with 0's become this value:
THRESH_SIGMA1 = 0.699471735


def close_holes(infile, cube_size, iterations, outfile):
    """
    Closes small holes in a binary volume by using a binary closing operation.

    Args:
        infile (str): input 'MRC' file with a binary volume
        cube_size (str): size of the cube used for the binary closing operation
            (dilation followed by erosion)
        iterations (int): number of closing iterations
        outfile (str): output 'MRC' file with the closed volume

    Returns:
        None
    """
    tomo = io.load_tomo(infile)
    data_type = tomo.dtype  # dtype('uint8')
    tomo_closed = ndimage.binary_closing(
        tomo, structure=np.ones((cube_size, cube_size, cube_size)),
        iterations=iterations).astype(data_type)
    io.save_numpy(tomo_closed, outfile)


def run_gen_surface(tomo, outfile_base, lbl=1, mask=True, other_mask=None,
                    save_input_as_vti=False, verbose=False, isosurface=False,
                    grow=0, sg=0, thr=1.0):
    """
    Runs pysurf_io.gen_surface function, which generates a VTK PolyData triangle
    surface for objects in a segmented volume with a given label.

    Removes triangles with zero area, if any are present, from the resulting
    surface.

    Args:
        tomo (str or numpy.ndarray): segmentation input file in one of the
            formats: '.mrc', '.em' or '.vti', or 3D array containing the
            segmentation
        outfile_base (str): the path and filename without the ending for saving
            the surface (ending '.surface.vtp' will be added automatically)
        lbl (int, optional): the label to be considered, 0 will be ignored,
            default 1
        mask (boolean, optional): if True (default), a mask of the binary
            objects is applied on the resulting surface to reduce artifacts
            (in case isosurface=False)
        other_mask (numpy.ndarray, optional): if given (default None), this
            segmentation is used as mask for the surface
        save_input_as_vti (boolean, optional): if True (default False), the
            input is saved as a '.vti' file ('<outfile_base>.vti')
        verbose (boolean, optional): if True (default False), some extra
            information will be printed out
        isosurface (boolean, optional): if True (default False), generate
            isosurface (good for filled segmentations) - last three parameters
            are used in this case
        grow (int, optional): if > 0 the surface is grown by so many voxels
            (default 0 - no growing)
        sg (int, optional): sigma for gaussian smoothing in voxels (default 0 -
            no smoothing)
        thr (optional, float): thr for isosurface (default 1.0)

    Returns:
        the triangle surface (vtk.PolyData)
    """
    t_begin = time.time()

    # Generating the surface (vtkPolyData object)
    if isosurface:
        surface = io.gen_isosurface(tomo, lbl, grow, sg, thr, mask=other_mask)
    else:
        surface = io.gen_surface(tomo, lbl, mask, other_mask, verbose=verbose)

    t_end = time.time()
    duration = t_end - t_begin
    print 'Surface generation took: %s min %s s' % divmod(duration, 60)

    # Writing the vtkPolyData surface into a VTP file
    io.save_vtp(surface, outfile_base + '.surface.vtp')
    print 'Surface was written to the file %s.surface.vtp' % outfile_base

    if save_input_as_vti is True:
        # If input is a file name, read in the segmentation array from the file:
        if isinstance(tomo, str):
            tomo = io.load_tomo(tomo)
        elif not isinstance(tomo, np.ndarray):
            raise pexceptions.PySegInputError(
                expr='run_gen_surface',
                msg='Input must be either a file name or a ndarray.')

        # Save the segmentation as VTI for opening it in ParaView:
        io.save_numpy(tomo, outfile_base + '.vti')
        print 'Input was saved as the file %s.vti' % outfile_base

    return surface


def tomo_smooth_surf(seg, sg, th):
    """
    Gets a smooth surface from a segmented region.

    Args:
        seg (numpy.ndarray): 3D segmentation array
        sg (int): sigma for gaussian smoothing (in voxels)
        th (float): iso-surface threshold

    Returns:
        a vtkPolyData with the surface found
    """

    # Smoothing
    seg_s = ndimage.filters.gaussian_filter(seg.astype(np.float), sg)
    seg_vti = io.numpy_to_vti(seg_s)

    # Iso-surface
    surfaces = vtk.vtkMarchingCubes()
    surfaces.SetInputData(seg_vti)
    surfaces.ComputeNormalsOn()
    surfaces.ComputeGradientsOn()
    surfaces.SetValue(0, th)
    surfaces.Update()

    # # Keep just the largest surface
    # con_filter = vtk.vtkPolyDataConnectivityFilter()
    # con_filter.SetInputData(surfaces.GetOutput())
    # con_filter.SetExtractionModeToLargestRegion()

    # return con_filter.GetOutput()

    return surfaces.GetOutput()


if __name__ == "__main__":
    fold = "/fs/pool/pool-ruben/Maria/curvature/Javier/SCS/171108_TITAN_l2_t4/"
    seg_file = "{}t4_ny01_lbl.labels_FILLED.mrc".format(fold)
    seg = io.load_tomo(seg_file)
    data_type = seg.dtype
    sg = 1
    thr = THRESH_SIGMA1
    outfile_base = "{}test_gen_isosurface/" \
                   "SCSl2t4_cER_sg{}_thr{}".format(fold, sg, thr)
    # Surface generation with filled segmentation using vtkMarchingCubes
    # and applying the mask of unfilled segmentation
    print ("\nMaking filled and unfilled binary segmentations...")
    # have to combine the outer and inner seg. for the filled one:
    filled_binary_seg = np.logical_or(seg == 2, seg == 3).astype(data_type)
    binary_seg = (seg == 2).astype(data_type)
    print ("\nGenerating a surface...")
    surf = run_gen_surface(
        filled_binary_seg, outfile_base, lbl=1, other_mask=binary_seg,
        isosurface=True, sg=sg, thr=thr)


    # in_seg = ("/fs/pool/pool-ruben/Maria/curvature/synthetic_volumes/"
    #           "cylinder_r10_h20.mrc")
    # tomo_seg = io.load_tomo(in_seg)
    # for seg_sg in [2]:  # in voxels (Johannes: 2)
    #     print "sigma = {}".format(seg_sg)
    #     for seg_th in [0.49]:  # (Johannes: 0.45)
    #         print "threshold = {}".format(seg_th)
    #         out_surf = ("/fs/pool/pool-ruben/Maria/curvature/synthetic_volumes/"
    #                     "cylinder_r10_h20.smooth_surface_sg{}_th{}.vtp".format(
    #                      seg_sg, seg_th))
    #         surf = tomo_smooth_surf(tomo_seg, seg_sg, seg_th)
    #         print "The surface has %s cells" % surf.GetNumberOfCells()
    #         print "%s points" % surf.GetNumberOfPoints()
    #         io.save_vtp(surf, out_surf)
