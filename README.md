# Training-Sample-Selection

The script is used to select deep learning training samples from a remote sensing image. 

## Background

In remote sensing deep learning segmentation, increasing the number of training samples typically improves model accuracy, but labeling image samples is a time-consuming and labor-intensive task. We propose a strategic sample selection method to identify the optimal number of samples, reducing the labeling effort while maintaining satisfactory model accuracy. 

## Usage

```python
python sampling.py --image_path D:\data\image.tif --lc_path D:\data\land_cover.tif --lc_target_value 1
```

## Implementation

**1. Data preparation**

Prepare the remote sensing image data of the study area along with the corresponding land cover products, ensuring both are in the same coordinate system. The remote sensing image will be converted to `uint8` format with `process_image=True` before further processing. 

**2. Generate candidate total samples**

The remote sensing images are cropped into candidate samples, which are then categorized based on two-dimensional metrics: percentage and edge intensity. 

- `sample_size` refers to the size of the image sample, with a default of 256×256 pixels. 

- `rgb_bands` refers to the channel number of the red, green, and blue bands in the remote sensing image, which are required for edge detection when extracting edge intensity from true-color images. 

- `zero_percent` is used to filter out samples consisting entirely of zeros. Samples are retained only if the percentage of zeros is below the threshold. 

**3. Select training samples**

Using the strategic sample selection method to select training samples, and the optimal sample size is 4%.

- `sample_percent` refers to the proportion of samples selected. According to our study, the optimal sample size is 4%. The default value is set to 0.04. 

![](https://github.com/Remote-Sensing-of-Land-Resource-Lab/Training-Sample-Selection/blob/main/figures/selection1.png)