import torch
from halonet_pytorch import HaloAttention

attn = HaloAttention(
    dim = 4064,         # dimension of feature map
    block_size = 8,    # neighborhood block size (feature map must be divisible by this)
    halo_size = 4,     # halo size (block receptive field)
    dim_head = 64,     # dimension of each head
    heads = 4          # number of attention heads
).cuda()

fmap = torch.randn(10, 4064, 32, 32).cuda()
attn(fmap) # (1, 512, 32, 32)