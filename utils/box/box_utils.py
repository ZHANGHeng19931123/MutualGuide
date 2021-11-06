#!/usr/bin/python
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import numpy as np


def point_form(boxes):
    """ Convert prior_boxes to (xmin, ymin, xmax, ymax) """

    return torch.cat((boxes[:, :2] - boxes[:, 2:] / 2, boxes[:, :2] + boxes[:, 2:] / 2), 1)


def center_size(boxes):
    """ Convert prior_boxes to (cx, cy, w, h) """

    return torch.cat(((boxes[:, 2:] + boxes[:, :2]) / 2, boxes[:, 2:] - boxes[:, :2]), 1)


def jaccard(box_a, box_b):
    """ Compute the jaccard overlap of two sets of boxes """

    A = box_a.size(0)
    B = box_b.size(0)
    max_xy = torch.min(box_a[:, 2:].unsqueeze(1).expand(A, B, 2), box_b[:, 2:].unsqueeze(0).expand(A, B, 2))
    min_xy = torch.max(box_a[:, :2].unsqueeze(1).expand(A, B, 2), box_b[:, :2].unsqueeze(0).expand(A, B, 2))
    inter = torch.clamp(max_xy - min_xy, min=0)
    inter = inter[:, :, 0] * inter[:, :, 1]
    area_a = ((box_a[:, 2] - box_a[:, 0]) * (box_a[:, 3] - box_a[:, 1])).unsqueeze(1).expand_as(inter)  # [A,B]
    area_b = ((box_b[:, 2] - box_b[:, 0]) * (box_b[:, 3] - box_b[:, 1])).unsqueeze(0).expand_as(inter)  # [A,B]
    union = area_a + area_b - inter
    return inter / union  # [A,B]


def match(truths, priors, labels, loc_t, conf_t, overlap_t, idx):
    """ Match each prior box with the ground truth box """

    overlaps = jaccard(truths, point_form(priors))
    (best_truth_overlap, best_truth_idx) = overlaps.max(0)
    (best_prior_overlap, best_prior_idx) = overlaps.max(1)
    best_truth_overlap.index_fill_(0, best_prior_idx, 1)  # ensure best prior
    for j in range(best_prior_idx.size(0)):
        best_truth_idx[best_prior_idx[j]] = j

    overlap_t[idx] = best_truth_overlap  # [num_priors] jaccord for each prior
    conf_t[idx] = labels[best_truth_idx]  # [num_priors] top class label for each prior
    loc_t[idx] = truths[best_truth_idx]  # Shape: [num_priors,4]


def mutual_match(truths, priors, regress, classif, labels, loc_t, conf_t, overlap_t, pred_t, idx, topk=15, sigma=2.0):
    """Classify to regress and regress to classify, Mutual Match for label assignement """

    num_obj = truths.size()[0]
    reg_overlaps = jaccard(truths, decode(regress, priors))
    pred_classifs = jaccard(truths, point_form(priors))
    classif = classif.sigmoid().t()[labels - 1, :]
    pred_classifs = pred_classifs ** ((sigma - classif + 1e-6) / sigma)
    reg_overlaps[reg_overlaps != reg_overlaps.max(dim=0, keepdim=True)[0]] = 0.0
    pred_classifs[pred_classifs != pred_classifs.max(dim=0, keepdim=True)[0]] = 0.0

    for (reg_overlap, pred_classif) in zip(reg_overlaps, pred_classifs):
        num_pos = max(1, torch.topk(reg_overlap, topk, largest=True)[0].sum().int())
        pos_mask = torch.topk(reg_overlap, num_pos, largest=True)[1]
        reg_overlap[pos_mask] += 3.0

        num_pos = max(1, torch.topk(pred_classif, topk, largest=True)[0].sum().int())
        pos_mask = torch.topk(pred_classif, num_pos, largest=True)[1]
        pred_classif[pos_mask] += 3.0

    ## for classification ###
    (best_truth_overlap, best_truth_idx) = reg_overlaps.max(dim=0)
    overlap_t[idx] = best_truth_overlap  # [num_priors] jaccord for each prior
    conf_t[idx] = labels[best_truth_idx]  # [num_priors] top class label for each prior
    ## for regression ###
    (best_truth_overlap, best_truth_idx) = pred_classifs.max(dim=0)
    pred_t[idx] = best_truth_overlap  # [num_priors] jaccord for each prior
    loc_t[idx] = truths[best_truth_idx]  # Shape: [num_priors,4]


def encode(matched, priors, variances=[0.1, 0.2]):
    """ Encode from the priorbox layers to ground truth boxes """

    g_cxcy = (matched[:, :2] + matched[:, 2:]) / 2 - priors[:, :2]
    g_cxcy /= variances[0] * priors[:, 2:]
    g_wh = (matched[:, 2:] - matched[:, :2]) / priors[:, 2:]
    g_wh = torch.log(g_wh) / variances[1]
    targets = torch.cat([g_cxcy, g_wh], 1)  # [num_priors,4]
    return targets


def decode(loc, priors, variances=[0.1, 0.2]):
    """ Decode locations from predictions using priors """

    boxes = torch.cat((priors[:, :2] + loc[:, :2] * variances[0] * priors[:, 2:], 
                       priors[:, 2:] * torch.exp(loc[:, 2:] * variances[1])), 1)
    boxes[:, :2] -= boxes[:, 2:] / 2
    boxes[:, 2:] += boxes[:, :2]
    return boxes
