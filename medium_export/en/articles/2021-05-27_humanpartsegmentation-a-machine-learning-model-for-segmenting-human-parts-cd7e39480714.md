---
title: "HumanPartSegmentation : A Machine Learning Model for Segmenting Human Parts"
author: "David Cochard"
date: 2021-05-27
lastmod: 2021-06-10
tags: [ailia-models, machine-learning, deep-learning, ai, segmentation]
original_url: https://medium.com/axinc-ai/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714
---

# HumanPartSegmentation : A Machine Learning Model for Segmenting Human Parts

# HumanPartSegmentation : A Machine Learning Model for Segmenting Human Parts

[![David Cochard](../images/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714/image_000.jpg)](/@cochard-dav?source=post_page---byline--cd7e39480714---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--cd7e39480714---------------------------------------)

4 min read

·

May 27, 2021

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dcd7e39480714&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fhumanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714&source=---header_actions--cd7e39480714---------------------post_audio_button------------------)

Share

This is an introduction to「HumanPartSegmentation」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

*Self-Correction for Human Parsing* is a machine learning model released by BaiduResearch in October of 2019 that can perform segmentation for different parts of a person.

[## Self-Correction for Human Parsing

### Labeling pixel-level masks for fine-grained semantic segmentation tasks, e.g. human parsing, remains a challenging…

arxiv.org](https://arxiv.org/abs/1910.09777?source=post_page-----cd7e39480714---------------------------------------)

[## PeikeLi/Self-Correction-Human-Parsing

### An out-of-box human parsing representation extractor. Our solution ranks 1st for all human parsing tracks (including…

github.com](https://github.com/PeikeLi/Self-Correction-Human-Parsing?source=post_page-----cd7e39480714---------------------------------------)

The following parts are supported.

> CATEGORY = (  
>  ‘Background’, ‘Hat’, ‘Hair’, ‘Glove’, ‘Sunglasses’, ‘Upper-clothes’, ‘Dress’, ‘Coat’,  
>  ‘Socks’, ‘Pants’, ‘Jumpsuits’, ‘Scarf’, ‘Skirt’, ‘Face’, ‘Left-arm’, ‘Right-arm’,  
>  ‘Left-leg’, ‘Right-leg’, ‘Left-shoe’, ‘Right-shoe’  
> )

Below is a result on an input image.

Press enter or click to view image in full size

![](../images/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714/image_001.jpeg)

Source：<https://github.com/PeikeLi/Self-Correction-Human-Parsing/blob/master/demo/demo.jpg>

Press enter or click to view image in full size

![](../images/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714/image_002.png)

Inference result

## Architecture

*HumanPartSegmentation* has been trained from 50,000 images of the [*LIP dataset*](http://sysu-hcp.net/lip/), but this dataset presents some challenges. In normal segmentation, all the pixels belonging to one instance share the same semantic label, but in human part segmentation, ambiguous boundaries between different semantic parts makes the cost of annotating higher, and often result in noise and mislabeling in the Ground Truth (GT) data.

Press enter or click to view image in full size

![](../images/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714/image_003.png)

Example of noise in the GT data (Source：<https://arxiv.org/pdf/1910.09777.pdf>）

In *Self-Correction for Human Parsing (SCHP)*, it is assumed that the dataset contains noise, and a specific loss function is applied to edges to generate class-agnostic boundaries, combined with a self-correction method used to refine GT label data to achieve more accurate segmentation.

The network architecture uses *resnet101* as the backbone and is known as *Context Embedding with Edge Perceiving (CE2P)*. *CE2P* wasfirst introduced in [*Devil in the Details: Towards Accurate Single and Multiple Human Parsing*](https://arxiv.org/abs/1809.05996)published in September 2018, which uses a method to improve accuracy by applying a specific loss function on edges between parts of the segmentation. Traditionally, learning is based on the assumption that the GT data is correct, but CE2P assumes that the GT segmentation contains noise, and deals data accordingly.

[## Devil in the Details: Towards Accurate Single and Multiple Human Parsing

### Human parsing has received considerable interest due to its wide application potentials. Nevertheless, it is still…

arxiv.org](https://arxiv.org/abs/1809.05996?source=post_page-----cd7e39480714---------------------------------------)

Press enter or click to view image in full size

![](../images/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714/image_004.png)

Source: <https://arxiv.org/pdf/1910.09777.pdf>

One of the characteristic SCHP is the use of a self-correcting learning cycle to modify the labels of the ground truth data as they learn. As shown in [*Distilling the Knowledge in a Neural Network*](https://medium.com/r?url=https%3A%2F%2Farxiv.org%2Fabs%2F1503.02531) published in March 2015, multiclass labels are known to contain *dark knowledge*. By using *pseudo-masks*, you can generate *soft-target labels* that contain *dark knowledge*, as opposed to one-hot labels that contain only the correct answer labels.

[## Distilling the Knowledge in a Neural Network

### A very simple way to improve the performance of almost any machine learning algorithm is to train many different models…

arxiv.org](https://arxiv.org/abs/1503.02531?source=post_page-----cd7e39480714---------------------------------------)

SCHP generates less noisy *teacher labels,* from the perspective of *distillation*, and a more accurate model by repeatedly training on GT labels, then re-labeling with the trained model, and training again using those new labels.

Press enter or click to view image in full size

![](../images/humanpartsegmentation-a-machine-learning-model-for-segmenting-human-parts-cd7e39480714/image_005.png)

The generated model was awarded at the *CVPR 2019 LIP Challenge*.

## Usage

You can use the following command to run HumanPartSegmentation on the webcam video stream in ailia SDK.

```
$ python3 human_part_segmentation.py -v 0
```

Here are some results.

[## axinc-ai/ailia-models

### (Image from https://github.com/PeikeLi/Self-Correction-Human-Parsing/blob/master/demo/demo.jpg) Shape : (1, 3, 473…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/image_segmentation/human_part_segmentation?source=post_page-----cd7e39480714---------------------------------------)

## Related topic

[## DPT : Segmentation Model Using Vision Transformer

### This is an introduction to「DPT」, a machine learning model that can be used with ailia SDK. You can easily use this…

medium.com](/axinc-ai/dpt-segmentation-model-using-vision-transformer-b479f3027468?source=post_page-----cd7e39480714---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.