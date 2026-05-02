---
title: "AnimalPose : Pose Esimation for Animals"
author: "David Cochard"
date: 2021-07-01
lastmod: 2021-07-01
tags: [ailia-models, machine-learning, deep-learning, ai, pose-estimation]
original_url: https://medium.com/axinc-ai/animalpose-pose-esimation-for-animals-700603e0dbae
---

# AnimalPose : Pose Esimation for Animals

# AnimalPose : Pose Esimation for Animals

[![David Cochard](../images/animalpose-pose-esimation-for-animals-700603e0dbae/image_000.jpg)](/@cochard-dav?source=post_page---byline--700603e0dbae---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--700603e0dbae---------------------------------------)

2 min read

·

Jul 1, 2021

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D700603e0dbae&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fanimalpose-pose-esimation-for-animals-700603e0dbae&source=---header_actions--700603e0dbae---------------------post_audio_button------------------)

Share

This is an introduction to「AnimalPose」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

*AnimalPose* takes an image of an animal as input and computes a skeleton made of 20 keypoints. Since the model works on cows, it could for example be used in the field of agriculture.

Press enter or click to view image in full size

![](../images/animalpose-pose-esimation-for-animals-700603e0dbae/image_001.png)

Source: <https://pixabay.com/ja/photos/%e7%89%9b-%e5%ae%b6%e7%95%9c-%e4%b9%b3%e7%89%9b-%e4%b9%b3%e7%94%a8%e7%89%9b-%e5%8b%95%e7%89%a9-5717276/>

[## open-mmlab/mmpose

### English | 简体中文 MMPose is an open-source toolbox for pose estimation based on PyTorch. It is a part of the OpenMMLab…

github.com](https://github.com/open-mmlab/mmpose?source=post_page-----700603e0dbae---------------------------------------)

## Architecture

*AnimalPose* is published as part of mmpose, a general-purpose pose estimation framework. Two pre-trained models of *AnimalPose* are provided, one using *hrnet* and the other using *pose\_resnet*.

[## Animal — MMPose 0.15.0 documentation

### Edit description

mmpose.readthedocs.io](https://mmpose.readthedocs.io/en/latest/topics/animal.html?source=post_page-----700603e0dbae---------------------------------------)

Both models are based on a *Top-down* approach, which detects the keypoints of a single animal at a time. Animals are first detected using object detection models such as [*YOLO*](/axinc-ai/yolov5-the-latest-model-for-object-detection-b13320ec516b), and then the keypoints of each animal are computed by *AnimalPose*. More details on the difference between *Top-down* and *Bottom-up* approaches [here](/axinc-ai/poseresnet-a-top-down-machine-learning-model-for-skeletal-detection-9454f391ae4d).

## Dataset

*AnimalPose* was trained using *Animal-Pose Dataset,* which has been partially created based on PASCAL2011 dataset annotations and images.

The dataset contains more than 3000 images annotated in five categories, with a total of 5517 instances. Each instance has 20 key points defined: 4 paws, 2 eyes, 2 ears, 4 elbows, nose, throat, withers, tail base, and 4 knees points.

Press enter or click to view image in full size

![](../images/animalpose-pose-esimation-for-animals-700603e0dbae/image_002.png)

Source: <https://sites.google.com/view/animal-pose/>

[## Cross-Domain Adaptation for Animal Pose Estimation

### In this paper, we are interested in pose estimation of animals. Animals usually exhibit a wide range of variations on…

arxiv.org](https://arxiv.org/abs/1908.05806v2?source=post_page-----700603e0dbae---------------------------------------)

## Usage

Use the following command to run *AnimalPose* on a video file.

```
$ python3 animalpose.py -v input.mp4
```

[## axinc-ai/ailia-models

### (Image from…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/pose_estimation/animalpose?source=post_page-----700603e0dbae---------------------------------------)

Here is a result example.

## Related topics

[## BlazePose : A 3D Pose Estimation Model

### This is an introduction to「BlazePose」, a machine learning model that can be used with ailia SDK. You can easily use…

medium.com](/axinc-ai/blazepose-a-3d-pose-estimation-model-d8689d06b7c4?source=post_page-----700603e0dbae---------------------------------------)

[## LightWeightHumanPose : A Machine Learning Model for Fast Multi-person Pose Estimation.

### This is an introduction to「LightWeightHumanPose」, a machine learning model that can be used with ailia SDK. You can…

medium.com](/axinc-ai/lightweighthumanpose-a-machine-learning-model-for-fast-multi-person-skeleton-detection-631c042bed50?source=post_page-----700603e0dbae---------------------------------------)

[## PoseResnet : A Top-down Machine Learning Model for Pose Estimation

medium.com](/axinc-ai/poseresnet-a-top-down-machine-learning-model-for-skeletal-detection-9454f391ae4d?source=post_page-----700603e0dbae---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.