import os
import numpy as np
import random
import re
import shutil


def sample_select(sample_count,
                  temp_folder,
                  sample_folder,
                  sample_percent=0.03,
                  delete_temp_folder=True):
    file_number = np.sum(sample_count)
    select_number = np.ceil(file_number * sample_percent)
    select_number = int(select_number)
    print('select sample number: {} [{}%]'.format(select_number, sample_percent * 100))

    class_number = np.ceil(select_number / 9)
    count_list = sample_count.flatten()
    class_list = ['t1e1', 't1e2', 't1e3', 't2e1', 't2e2', 't2e3', 't3e1', 't3e2', 't3e3']

    # sort
    sorted_indices = np.argsort(count_list)
    count_list_sorted = [count_list[i] for i in sorted_indices]
    class_list_sorted = [class_list[i] for i in sorted_indices]

    # select sample number for each class
    select_list = []
    remain_number = select_number
    for num in count_list_sorted:
        if num <= class_number:
            select_list.append(int(num))
            remain_number = int(remain_number - num)
            remain_len = 9 - len(select_list)
            class_number = np.ceil(remain_number / remain_len)
        else:
            remain_len = 9 - len(select_list)
            class_number = np.ceil(remain_number / remain_len)
            select_list.extend([int(class_number)] * remain_len)
            break
    print('actual sample numbers:', np.sum(select_list))

    # sort as class_list
    mapping = {key: value for key, value in zip(class_list_sorted, select_list)}
    select_list_sorted = [mapping[key] for key in class_list]
    # print(class_list)
    # print(select_list_sorted)

    # ----- After determine sample number, list samples for each class -----
    folder_files = os.listdir(temp_folder)
    tif_files = [file for file in folder_files if file.endswith('.tif')]
    random.shuffle(tif_files)

    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    list7 = []
    list8 = []
    list9 = []

    for i in range(len(tif_files)):
        tif_name = tif_files[i]
        match_t = re.search(r't(\d+)', tif_name)
        match_e = re.search(r'e(\d+)', tif_name)

        if match_t:
            t = int(match_t.group(1))
        else:
            raise ValueError('tif name:', tif_name, i)
        if match_e:
            e = int(match_e.group(1))
        else:
            raise ValueError('tif name:', tif_name, i)

        if (t == 1) & (e == 1):
            if len(list1) < select_list_sorted[0]:
                list1.append(tif_name)
        elif (t == 1) & (e == 2):
            if len(list2) < select_list_sorted[1]:
                list2.append(tif_name)
        elif (t == 1) & (e == 3):
            if len(list3) < select_list_sorted[2]:
                list3.append(tif_name)
        elif (t == 2) & (e == 1):
            if len(list4) < select_list_sorted[3]:
                list4.append(tif_name)
        elif (t == 2) & (e == 2):
            if len(list5) < select_list_sorted[4]:
                list5.append(tif_name)
        elif (t == 2) & (e == 3):
            if len(list6) < select_list_sorted[5]:
                list6.append(tif_name)
        elif (t == 3) & (e == 1):
            if len(list7) < select_list_sorted[6]:
                list7.append(tif_name)
        elif (t == 3) & (e == 2):
            if len(list8) < select_list_sorted[7]:
                list8.append(tif_name)
        elif (t == 3) & (e == 3):
            if len(list9) < select_list_sorted[8]:
                list9.append(tif_name)
        else:
            raise ValueError('t:', t, 'e:', e, tif_name, i)

    list_select = list1 + list2 + list3 + list4 + list5 + list6 + list7 + list8 + list9

    os.makedirs(sample_folder, exist_ok=True)
    for idx, file in enumerate(list_select):
        source_path = os.path.join(temp_folder, file)
        target_path = os.path.join(sample_folder, file)
        shutil.copy(source_path, target_path)
        print('\r' + 'Selecting samples ... [{}/{}]'.format(idx + 1, len(list_select)), end='')

    if delete_temp_folder:
        shutil.rmtree(temp_folder)

    print('\r' + 'Training Samples have been select in {}'.format(sample_folder))
