import os
from osgeo import gdal
import numpy as np
from .array_proj import array_proj


def land_cover_clip(img_path, lc_path, lc_save_path):
    img_ds = gdal.Open(img_path)
    lc_ds = gdal.Open(lc_path)
    img_geo = img_ds.GetGeoTransform()

    extent = [img_geo[0],
              img_geo[3],
              img_geo[0] + img_geo[1] * img_ds.RasterXSize,
              img_geo[3] + img_geo[5] * img_ds.RasterYSize]

    options = gdal.WarpOptions(outputBounds=extent)
    gdal.Warp(lc_save_path, lc_ds, options=options)


def land_cover_process(img_path, lc_path, lc_save_path, class_value):
    """
    Clip the land cover to image extent, and extract the target class.
    :param img_path:
    :param lc_path:
    :param lc_save_path:
    :param class_value: the target class value in land cover
    :return:
    """
    # clip land cover to image extent
    assert '.tif' in img_path
    assert '.tif' in lc_path
    print('Processing land cover ... :', lc_path, end='')

    lc_template_path = lc_save_path[:-4] + '_temp.tif'
    land_cover_clip(img_path, lc_path, lc_template_path)

    # transfer to 0/255
    lc_ds = gdal.Open(lc_template_path)
    lc_geo = lc_ds.GetGeoTransform()
    lc_proj = lc_ds.GetProjection()

    lc = lc_ds.ReadAsArray()
    del lc_ds
    lc = np.where(lc == class_value, 1, 0)
    lc = (lc * 255).astype(np.uint8)
    array_proj(lc, lc_save_path, lc_geo, lc_proj)

    os.remove(lc_template_path)
    print('\r' + 'Land cover saved (True=255):', lc_path)
