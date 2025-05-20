import click
from func.data_preparation import image_process, land_cover_process
from func.sample_temp import sample_crop, level_table
from func.sample_selection import sample_select


@click.command()
@click.option('--image_path',
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              required=True,
              help='Remote sensing image for sample selection.')
@click.option('--lc_path',
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              required=True,
              help='Land cover data corresponding to teh remote sensing image.')
@click.option('--lc_target_value',
              type=int,
              required=True,
              help='Value of the target class in the land cover data.')
@click.option('--sample_folder', type=click.Path(exists=False), default=r'.\samples',
              help='Folder where the selected samples saved.')
@click.option('--process_image', type=click.BOOL, default=True,
              help='Whether the image is processed.')
@click.option('--image_process_path', type=click.Path(exists=False), default=r'.\image.tif',
              help='Path where the image saved after processing.')
@click.option('--lc_process_path', type=click.Path(exists=False), default=r'.\land_cover.tif',
              help='Path where the land cover data saved after processing.')
@click.option('--temp_folder', type=click.Path(exists=False), default=r'.\temp',
              help='Temporary folder for all samples.')
@click.option('--sample_prefix', type=str, default='sample',
              help='Prefix for sample names.')
@click.option('--rgb_bands', type=list, default=[2, 1, 0],
              help='Band indices corresponding to the RGB bands in the image.')
@click.option('--sample_size', type=int, default=256,
              help='Size of the sample (bands, size, size)')
@click.option('--zero_percent', type=float, default=0.2,
              help='Save samples that are all 0 (no data in image) with the probability, values (0-1).')
@click.option('--sample_percent', type=float, default=0.025,
              help='Percentage of samples selected, values (0-1).')
@click.option('--delete_temp_tif', type=click.BOOL, default=True,
              help='Whether to delete the image and land cover data generated after processing')
@click.option('--delete_temp_folder', type=click.BOOL, default=True,
              help='Whether to delete the temporary folder')
def sampling(image_path,
             lc_path,
             lc_target_value,
             sample_folder,
             process_image,
             image_process_path,
             lc_process_path,
             temp_folder,
             sample_prefix,
             rgb_bands,
             sample_size,
             zero_percent,
             sample_percent,
             delete_temp_tif,
             delete_temp_folder):
    print('-' * 10, '1. data preparation', '-' * 10)
    if process_image:
        image_process(image_path, image_process_path)
    else:
        image_process_path = image_path
        delete_temp_tif = False
    land_cover_process(image_process_path, lc_path, lc_process_path, lc_target_value)

    print('-' * 10, '2. sample crop', '-' * 10)
    sample_crop(image_process_path, lc_process_path, temp_folder,
                sample_prefix, rgb_bands, sample_size, zero_percent, delete_temp_tif)
    sample_count = level_table(temp_folder)

    print('-' * 10, '3. sample select', '-' * 10)
    sample_select(sample_count, temp_folder, sample_folder, sample_percent, delete_temp_folder)
    _ = level_table(sample_folder)


if __name__ == '__main__':
    sampling()
