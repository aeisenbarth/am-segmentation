import logging
from pathlib import Path
from shutil import rmtree

import cv2
import numpy as np
import torch
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader

logger = logging.getLogger('am-segm')


def read_image(path):
    return cv2.imread(str(path))[:,:,0]  # because ch0==ch1==ch2


def convert_to_image(array):
    if type(array) == torch.Tensor:
        image = array.detach().cpu().numpy()
    else:
        image = array
    if image.ndim == 4:
        image = image[0][0]
    elif image.ndim == 3:
        image = image[0]
    return image


def plot_images_row(images, titles=None):

    def plot(axis, image, title=None):
        image = convert_to_image(image)
        if image.ndim > 2:
            image = image[0]
        axis.imshow(image)
        if title:
            axis.set_title(title)

    n = min(len(images), 4)
    fig, axes = plt.subplots(1, n, figsize=(16, 8))
    if type(axes) == list:
        for i in range(n):
            plot(axes[i], images[i], titles[i] if titles else None)
    else:
        plot(axes, images[0], titles[0] if titles else None)
    return fig


def plot_overlay(image, mask, figsize=(10, 10)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    image, mask = np.array(image), np.array(mask)
    if image.ndim > 2:
        image = image[0]  # plot first channel only
    if mask.ndim > 2:
        mask = mask[0]  # plot first channel only
    ax.imshow(image, cmap='gray', interpolation=None)  # plot first channel only
    ax.imshow(mask, cmap='jet', interpolation=None, alpha=0.5)
    return fig


def overlay_images_with_masks(path, image_ext='png'):
    for group_path in path.iterdir():
        logger.info(f'Overlaying: {group_path}')
        mask = read_image(str(group_path / f'mask.{image_ext}'))
        image = read_image(str(group_path / f'source.{image_ext}'))
        assert image.shape == mask.shape

        fig = plot_overlay(image, mask)
        plt.savefig(group_path / f'overlay.{image_ext}', dpi=600, bbox_inches='tight')
        plt.close()