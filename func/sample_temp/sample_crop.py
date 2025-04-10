import os
from osgeo import gdal
import numpy as np
from skimage import feature, color
from func.data_preparation import array_proj


def level_target(sample, sample_geo, lc, lc_geo):
    """
    use land cover data
    """
    C, H, W = sample.shape
    extent = [sample_geo[0], sample_geo[0] + W * sample_geo[1],
              sample_geo[3], sample_geo[3] + H * sample_geo[5]]

    h1, h2 = extent[2], extent[3]
    w1, w2 = extent[0], extent[1]

    h1 = np.abs((h1 - lc_geo[3]) / lc_geo[5])
    h2 = np.abs((h2 - lc_geo[3]) / lc_geo[5])
    w1 = np.abs((w1 - lc_geo[0]) / lc_geo[1])
    w2 = np.abs((w2 - lc_geo[0]) / lc_geo[1])

    if h1 > h2:
        h1, h2 = h2, h1
    if w1 > w2:
        w1, w2 = w2, w1

    h1 = int(np.max([np.floor(h1), 0]))
    h2 = int(np.min([np.ceil(h2) + 1, lc.shape[0]]))
    w1 = int(np.max([np.floor(w1), 0]))
    w2 = int(np.min([np.ceil(w2) + 1, lc.shape[1]]))

    target_area = lc[h1:h2, w1:w2]
    target_level = np.sum(target_area / 255) / (target_area.shape[0] * target_area.shape[1])

    entropy = cross_entropy(target_level)
    return entropy


def cross_entropy(p, epsilon=1e-10):
    assert 0 <= p <= 1, 'p should be in [0, 1]'
    p = np.clip(p, epsilon, 1. - epsilon)
    q = 1 - p
    entropy = - p * np.log2(p) - q * np.log2(q)
    return entropy


def level_edge(sample, sigma=2.0, f=10):
    """
    canny edge detection
    """
    gray = sample.copy()
    if len(sample.shape) == 3:
        C, H, W = sample.shape
        assert C == 3
        gray = color.rgb2gray(gray.transpose(1, 2, 0))  # (h, w, c)
    elif len(sample.shape) == 2:
        H, W = sample.shape
        if np.max(gray) > 1:
            gray = gray / np.max(gray)
        gray = gray.astype(np.float64)

    edges = feature.canny(gray, sigma=sigma)
    edge_level = f * edges.sum() / (H * W)
    return edge_level


def class_by_level(temp_folder, image_list,
                   target_list, edge_list,
                   q1=0.05, q2=0.95):
    file_number = len(image_list)
    t_min = np.quantile(target_list, q1)
    t_max = np.quantile(target_list, q2)
    e_min = np.quantile(edge_list, q1)
    e_max = np.quantile(edge_list, q2)

    t_l = (t_max - t_min) / 3.
    e_l = (e_max - e_min) / 3.
    t_l1, t_l2 = t_min + t_l, t_min + 2 * t_l
    e_l1, e_l2 = e_min + e_l, e_min + 2 * e_l
    # print('target [{:.5f} {:.5f}]  edge [{:.5f} {:.5f}]'.format(t_l1, t_l2, e_l1, e_l2))

    for i in range(file_number):
        image_name = image_list[i]
        image_path = os.path.join(temp_folder, image_name)

        t_value, e_value = target_list[i], edge_list[i]

        if 0. <= t_value < t_l1:
            target_level = 1
        elif t_l1 <= t_value < t_l2:
            target_level = 2
        elif t_value >= t_l2:
            target_level = 3
        else:
            raise ValueError('target value error -- idx:{} t:{}'.format(i, t_value))

        if e_value < e_l1:
            edge_level = 1
        elif e_l1 <= e_value < e_l2:
            edge_level = 2
        elif e_value >= e_l2:
            edge_level = 3
        else:
            raise ValueError('edge value error -- idx:{} e:{}'.format(i, e_value))

        new_name = image_name[:-4] + '_t{0:01d}e{1:01d}.tif'.format(target_level, edge_level)
        new_path = os.path.join(temp_folder, new_name)
        os.rename(image_path, new_path)
        print('\r' + '[{0}/{1}] {2} t:{3:.4f} e:{4:.4f}'
              .format(i + 1, file_number, new_name, t_value, e_value), end='')
    print('\n', end='')


def sample_crop(image_path,
                lc_path,
                temp_folder,
                sample_prefix='sample',
                rgb_bands=None,
                sample_size=256,
                zero_percent=0.2,
                delete_temp_tif=True):
    if rgb_bands is None:
        rgb_bands = [2, 1, 0]
    assert len(rgb_bands) == 1 or 3

    image_ds = gdal.Open(image_path)
    image_geo = image_ds.GetGeoTransform()
    image_proj = image_ds.GetProjection()
    image = image_ds.ReadAsArray()  # (c, h, w)
    del image_ds
    print('image', image.shape)

    lc_ds = gdal.Open(lc_path)
    lc_geo = lc_ds.GetGeoTransform()
    lc = lc_ds.ReadAsArray()
    del lc_ds

    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)

    C, H, W = image.shape
    rows = (H - sample_size) // sample_size + 1
    cols = (W - sample_size) // sample_size + 1

    image_list = []
    target_list = []
    edge_list = []
    count = 0

    # ----- First loop: level value recording -----
    for i in range(rows):
        for j in range(cols):
            x1 = i * sample_size
            x2 = i * sample_size + sample_size
            y1 = j * sample_size
            y2 = j * sample_size + sample_size
            sample = image[:, x1:x2, y1:y2]

            sample_zero = np.all(sample == 0, axis=0).astype(np.uint8)
            if np.sum(sample_zero) < zero_percent * sample_size ** 2:  # ignore samples with too many 0
                geo_sample = list(image_geo)
                geo_sample[0] = geo_sample[0] + y1 * geo_sample[1]  # geo[0] -> width
                geo_sample[3] = geo_sample[3] + x1 * geo_sample[5]

                # save samples
                save_name = '{0}_h{1:03d}w{2:03d}.tif'.format(sample_prefix, i, j)
                save_path = os.path.join(temp_folder, save_name)
                array_proj(sample, save_path, geo_sample, image_proj)

                # level rate
                sample_rgb = sample[rgb_bands, :, :]
                target_level = level_target(sample, geo_sample, lc, lc_geo)
                edge_level = level_edge(sample_rgb)

                image_list.append(save_name)
                target_list.append(target_level)
                edge_list.append(edge_level)

                count += 1
                print('\r' + '<{}> {} {} target:{:.4f} edge:{:.4f}'
                      .format(count, save_name, sample.shape, target_level, edge_level), end='')

    # ----- Second loop: classify according to level value -----
    class_by_level(temp_folder, image_list, target_list, edge_list)

    if delete_temp_tif:
        os.remove(image_path)
        os.remove(lc_path)
