import os
from osgeo import gdal, gdalconst
import numpy as np
from .array_proj import array_proj


def image_stretch_2d(image, tmin, tmax):
    """
    (h, w) -> 255 uint8
    """
    image = np.nan_to_num(image, nan=0)  # transform nan to 0
    image_mask = np.where(image == 0, 0, 1).astype(np.uint8)

    image = (image.astype(np.float32) - tmin) / (tmax - tmin)
    image = np.maximum(np.minimum(image * 255, 255), 0).astype(np.uint8)
    image = image * image_mask

    return image


def image_stretch(image, min_list, max_list):
    """
    (c, h, w) -> uint8
    """
    if len(image.shape) == 3:
        c, h, w = image.shape
        image_bands = [image_stretch_2d(image[i, :, :], min_list[i], max_list[i]) for i in range(c)]
        image = np.stack(image_bands, axis=0)
    elif len(image.shape) == 2:
        image = image_stretch_2d(image, min_list[0], max_list[0])
    return image.astype(np.uint8)


def merge_two_tif(tif_path1, tif_path2, save_path):
    tif_ds1 = gdal.Open(tif_path1, gdal.GA_ReadOnly)
    tif_ds2 = gdal.Open(tif_path2, gdal.GA_ReadOnly)
    raster_list = [tif_ds1, tif_ds2]

    input_raster_file1 = raster_list[0]
    inputProj1 = input_raster_file1.GetProjection()
    if 'int8' in input_raster_file1.ReadAsArray().dtype.name:
        datatype = gdalconst.GDT_Byte
    elif 'int16' in input_raster_file1.ReadAsArray().dtype.name:
        datatype = gdalconst.GDT_UInt16
    else:
        datatype = gdalconst.GDT_Float32

    options = gdal.WarpOptions(srcSRS=inputProj1,
                               dstSRS=inputProj1,
                               format='GTiff',
                               resampleAlg=gdalconst.GRA_Bilinear,
                               outputType=datatype)

    gdal.Warp(save_path, raster_list, options=options)
    del raster_list


def image_process(img_path, save_path, q1=0.02, q2=0.98):
    """
    Stretch the remote sensing image and save it in uint8 format.
    :param img_path: remote sensing image path
    :param save_path: save path
    :param q1:
    :param q2:
    :return:
    """
    assert '.tif' in img_path
    assert '.tif' in save_path
    img_ds = gdal.Open(img_path)
    img_geo = img_ds.GetGeoTransform()
    img_proj = img_ds.GetProjection()

    print('Processing image ... :', img_path, end='')

    image = img_ds.ReadAsArray()  # (c, h, w)
    del img_ds
    C, H, W = image.shape
    # print('image', image.shape, np.max(image), image.dtype)

    image = np.nan_to_num(image, nan=0)  # transform nan to 0
    img_list = np.split(image, C, axis=0)
    min_list = [np.quantile(r[r != 0], q1) for r in img_list]
    max_list = [np.quantile(r[r != 0], q2) for r in img_list]
    # print(min_list, max_list)
    del img_list

    """ Avoiding memory shortage """
    image1 = image[:, :, :(W // 2)]
    image2 = image[:, :, (W // 2):]
    del image

    # --- image 1 ---
    image1 = image_stretch(image1, min_list, max_list)
    array_proj(image1, save_path[:-4] + '_temp1.tif', img_geo, img_proj)
    del image1

    # --- image 2 ---
    clip_geo = list(img_geo)
    clip_geo[0] = img_geo[0] + (W // 2) * img_geo[1]
    image2 = image_stretch(image2, min_list, max_list)
    array_proj(image2, save_path[:-4] + '_temp2.tif', clip_geo, img_proj)
    del image2

    # ----- merge -----
    merge_two_tif(save_path[:-4] + '_temp1.tif',
                  save_path[:-4] + '_temp2.tif',
                  save_path)
    os.remove(save_path[:-4] + '_temp1.tif')
    os.remove(save_path[:-4] + '_temp2.tif')
    print('\r' + 'Image saved (uint8):', save_path)
