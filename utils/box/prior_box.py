#!/usr/bin/python
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
import math
from math import sqrt as sqrt
from itertools import product as product


def PriorBox(base_anchor, size, base_size, multi_anchor=True, multi_level=True):
    """Predefined anchor boxes"""
    
    if not multi_level:
        feature_map = [math.ceil(size / 2 ** 4)]
    else:
        if base_size == 320:
            repeat = 4
        elif base_size == 512:
            repeat = 5
        else:
            raise ValueError('Error: Sorry size {} is not supported!'.format(base_size))
        feature_map = [math.ceil(size / 2 ** (3 + i)) for i in range(repeat)]

    mean = []
    for (k, (f_h, f_w)) in enumerate(zip(feature_map, feature_map)):
        for (i, j) in product(range(f_h), range(f_w)):
            
            cy = (i + 0.5) / f_h
            cx = (j + 0.5) / f_w

            anchor = base_anchor * 2 ** k / size
            mean += [cx, cy, anchor, anchor]
            if multi_anchor:
                mean += [cx, cy, anchor * sqrt(2), anchor / sqrt(2)]
                mean += [cx, cy, anchor / sqrt(2), anchor * sqrt(2)]
                anchor *= sqrt(2)
                mean += [cx, cy, anchor, anchor]
                mean += [cx, cy, anchor * sqrt(2), anchor / sqrt(2)]
                mean += [cx, cy, anchor / sqrt(2), anchor * sqrt(2)]

    output = torch.Tensor(mean).view(-1, 4)
    output.clamp_(max=1, min=0)
    return output
