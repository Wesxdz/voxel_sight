from __future__ import print_function, division
import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import faiss
from einops import rearrange
from config import *
import faiss

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

class VoxelHeightDataset(Dataset):
    """
    Monocular forward facing views of 64x64 voxel grid
    45, 115 x rotation
    -44 to 44 z rotation
    """
    
    def __init__(self, dataset_size, dir, transform=None):
        self.dataset_size = dataset_size
        self.dir = dir
        self.transform = transform

    def __len__(self):
        return self.dataset_size

    def get_camera_view(self, idx):
        img = io.imread(os.path.join(self.dir, "voxels_{}.png".format(idx)))
        cv = rearrange(img, 'h w c -> c h w')
        cv = np.delete(cv, 3, 0) # Remove alpha channel...
        # xt = rearrange(img, 'h w c -> (h w) c').astype('float32')
        # sq = faiss.ScalarQuantizer(screen_size[0], faiss.ScalarQuantizer.QT_4bit)
        # sq.train(xt)
        # codes = sq.compute_codes(xt)
        # print(codes.shape)
        return torch.from_numpy(cv.astype('float32'))

    def get_voxel_grid(self, idx):
        height_grid = torch.zeros(voxel_grid_size, dtype=torch.float32)
        reward_grid = torch.zeros(voxel_grid_size, dtype=torch.int32)
        with open(os.path.join(self.dir, "visible_elements_{}".format(idx))) as visible:
            lines = visible.readlines()
            for line in lines:
                data = [int(d) for d in line.split(",")]
                height_grid[data[0]] = data[1]
                reward_grid[data[0]] = data[2]
        return height_grid, reward_grid


    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        camera_view = self.get_camera_view(idx)
        # TODO: Use Faiss to generate k means so that the input data can use a color index byte to reduce input Tensor size while retaining color
        height_grid, reward_grid = self.get_voxel_grid(idx)

        sample = {'view':camera_view, 'grid':height_grid, 'rewards':reward_grid}

        if self.transform:
            sample = self.transform(sample)

        return sample

# Same as above, but rewards for predicting number of visible pixels on a given voxel rather than height
class VoxelVisibilityDataset(Dataset):
    
    def __init__(self, dataset_size, dir, transform=None):
        self.dataset_size = dataset_size
        self.dir = dir
        self.transform = transform

    def __len__(self):
        return self.dataset_size

    def get_camera_view(self, idx):
        img = io.imread(os.path.join(self.dir, "voxels_{}.png".format(idx)))
        cv = rearrange(img, 'h w c -> c h w')
        cv = np.delete(cv, 3, 0) # Remove alpha channel...
        return torch.from_numpy(cv.astype('float32'))

    def get_voxel_grid(self, idx):
        visibility_grid = torch.zeros(voxel_grid_size, dtype=torch.float32)
        reward_grid = torch.zeros(voxel_grid_size, dtype=torch.int32)
        with open(os.path.join(self.dir, "visible_elements_{}".format(idx))) as visible:
            lines = visible.readlines()
            for line in lines:
                data = [int(d) for d in line.split(",")]
                visibility_grid[data[0]] = data[2]
                reward_grid[data[0]] = data[2]
        return visibility_grid, reward_grid


    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        camera_view = self.get_camera_view(idx)
        # TODO: Use Faiss to generate k means so that the input data can use a color index byte to reduce input Tensor size while retaining color
        visibility_grid, reward_grid = self.get_voxel_grid(idx)

        sample = {'view':camera_view, 'grid':visibility_grid, 'rewards':reward_grid}

        if self.transform:
            sample = self.transform(sample)

        return sample