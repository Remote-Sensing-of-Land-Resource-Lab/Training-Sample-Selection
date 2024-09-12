import os
import re
import numpy as np
import pandas as pd


def level_table(sample_folder, print_data=True):
    folder_files = os.listdir(sample_folder)
    tif_files = [file for file in folder_files if file.endswith('.tif')]
    print(sample_folder, len(tif_files))

    count_t1e1 = 0
    count_t1e2 = 0
    count_t1e3 = 0
    count_t2e1 = 0
    count_t2e2 = 0
    count_t2e3 = 0
    count_t3e1 = 0
    count_t3e2 = 0
    count_t3e3 = 0

    for i in range(len(tif_files)):
        tif_name = tif_files[i]

        match_t = re.search(r't(\d+)', tif_name)
        match_e = re.search(r'e(\d+)', tif_name)

        if match_t:
            t_level = int(match_t.group(1))
        else:
            raise ValueError('tif name:', tif_name, i)

        if match_e:
            e_level = int(match_e.group(1))
        else:
            raise ValueError('tif name:', tif_name, i)

        if (t_level == 1) & (e_level == 1):
            count_t1e1 += 1
        elif (t_level == 1) & (e_level == 2):
            count_t1e2 += 1
        elif (t_level == 1) & (e_level == 3):
            count_t1e3 += 1
        elif (t_level == 2) & (e_level == 1):
            count_t2e1 += 1
        elif (t_level == 2) & (e_level == 2):
            count_t2e2 += 1
        elif (t_level == 2) & (e_level == 3):
            count_t2e3 += 1
        elif (t_level == 3) & (e_level == 1):
            count_t3e1 += 1
        elif (t_level == 3) & (e_level == 2):
            count_t3e2 += 1
        elif (t_level == 3) & (e_level == 3):
            count_t3e3 += 1
        else:
            raise ValueError('t:', t_level, 'e:', e_level, tif_name, i)

    data = np.array([[count_t1e1, count_t1e2, count_t1e3],
                     [count_t2e1, count_t2e2, count_t2e3],
                     [count_t3e1, count_t3e2, count_t3e3]])
    df = pd.DataFrame(data, index=['t1', 't2', 't3'], columns=['e1', 'e2', 'e3'])
    df['sum'] = df.sum(axis=1)
    df.loc['sum'] = df.sum(axis=0)
    if print_data:
        print(df)
    return data
