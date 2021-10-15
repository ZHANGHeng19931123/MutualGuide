<img align="center" src="https://github.com/zhangheng19931123/MutualGuide/blob/master/doc/mg.svg">

# Introduction
MutualGuidance is a compact object detector specially designed for embedded devices. Comparing to existing detectors, this repo contains two key features. 
Firstly, the Mutual Guidance mecanism assigns labels to the classification task based on the prediction on the localization task, and vice versa, alleviating the misalignment problem between both tasks; Secondly, the teacher-student prediction disagreements guides the knowledge transfer in a feature-based detection distillation framework, thereby reducing the performance gap between both models.
For more details, please refer to our [ACCV paper](https://openaccess.thecvf.com/content/ACCV2020/html/Zhang_Localize_to_Classify_and_Classify_to_Localize_Mutual_Guidance_in_ACCV_2020_paper.html) and [BMVC paper](https://www.bmvc2021.com/).

# Planning
- [x] Add [RepVGG](https://arxiv.org/abs/2101.03697) backbone.
- [x] Add [ShuffleNetV2](https://arxiv.org/abs/1807.11164) backbone.
- [x] Add **TensorRT** transform code for inference acceleration.
- [x] Add **draw** function to plot detection results.
- [x] Add **custom dataset** training (annotations in `XML` format).
- [ ] Add [Transformer](https://arxiv.org/abs/2102.12122) backbone.
- [ ] Add [BiFPN](https://arxiv.org/abs/1911.09070) neck.


# Benchmark

| **Backbone** | **Resolution** | **AP<sup>val**<br>0.5:0.95 | **AP<sup>val**<br>0.5 | **AP<sup>val**<br>0.75 | **Speed V100**<br>(ms) | **Weights** |
|:------------:|:--------------:|:--------------------------:|:---------------------:|:----------------------:|:----------------------:|:-----------:|
| RepVGG-A1      | 320x320      | 39.9 | 57.2 | 42.7 | 3.6 | [Download](https://drive.google.com/file/d/1857V3PxW0UXvcL3aagOL_MTKWzY985Bc/view?usp=sharing) |
| ResNet-18      | 512x512      | 42.9 | 60.7 | 46.2 | 4.4 | [Download](https://drive.google.com/file/d/1bilD6E3tdjJI3ZD4vZ6nUU_eSsieAfm5/view?usp=sharing) |
| RepVGG-A1      | 512x512      | 44.0 | 62.1 | 47.3 | 4.4 | [Download](https://drive.google.com/file/d/1hsb_rxArYYCHK7_RJ37k0N_1uZRu2WmG/view?usp=sharing) |

**Remarks:**

- The inference runtime is measured by Pytorch framework on a Tesla V100 GPU, note that the post-processing time (NMS) time is not included.

# Datasets

First download the VOC and COCO dataset, you may find the sripts in `data/scripts/` helpful.
Then create a folder named `datasets` and link the downloaded datasets inside:

```Shell
$ mkdir datasets
$ ln -s /path_to_your_voc_dataset datasets/VOCdevkit
$ ln -s /path_to_your_coco_dataset datasets/coco2017
```
For training on custom dataset, first modify the dataset path `XMLroot` and categories `XML_CLASSES` in `data/xml_dataset.py`. Then apply `--dataset XML`.

# Training

For training with Mutual Guide:
```Shell
$ python3 train.py --neck ssd --backbone vgg16    --dataset VOC --size 320 --multi_level --multi_anchor --mutual_guide --pretrained
                          fpn            resnet34           COCO       512
                          pafpn          repvgg-A2          XML
                                         shufflenet-1.0
```

For knowledge distillation using PDF-Fistil:
```Shell
$ python3 distil.py --neck ssd --backbone vgg11    --dataset VOC --size 320 --multi_level --multi_anchor --mutual_guide --pretrained --kd pdf
                           fpn            resnet18           COCO       512
                           pafpn          repvgg-A1          XML
                                          shufflenet-0.5
```

**Remarks:**

- For training without MutualGuide, just remove the '--mutual_guide';
- For knowledge distillation with traditional MSE loss, just use parameter '--kd mse';
- The default folder to save trained model is `weights/`.

# Evaluation

Every time you want to evaluate a trained network:
```Shell
$ python3 test.py --neck ssd --backbone vgg11    --dataset VOC --size 320 --trained_model path_to_saved_weights --draw
                         fpn            resnet18           COCO       512
                         pafpn          repvgg-A1          XML
                                        shufflenet-0.5
```

**Remarks:**

- It will directly print the mAP, AP50 and AP50 results on VOC2007 Test or COCO2017 Val.
- Add parameter `--draw` to draw detection results. They will be saved in `draw/VOC/` or `draw/COCO/` or `draw/XML/`.

## Citing us
Please cite our papers in your publications if they help your research:

    @InProceedings{Zhang_2020_ACCV,
        author    = {Zhang, Heng and Fromont, Elisa and Lefevre, Sebastien and Avignon, Bruno},
        title     = {Localize to Classify and Classify to Localize: Mutual Guidance in Object Detection},
        booktitle = {Proceedings of the Asian Conference on Computer Vision (ACCV)},
        month     = {November},
        year      = {2020}
    }

    @InProceedings{Zhang_2021_BMVC,
        author    = {Zhang, Heng and Fromont, Elisa and Lefevre, Sebastien and Avignon, Bruno},
        title     = {PDF-Distil: including Prediction Disagreements in Feature-based Distillation for object detection},
        booktitle = {Proceedings of the British Machine Vision Conference (BMVC)},
        month     = {November},
        year      = {2021}
    }