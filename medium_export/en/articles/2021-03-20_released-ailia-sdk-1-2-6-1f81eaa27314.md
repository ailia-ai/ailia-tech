---
title: "Released ailia SDK 1.2.6"
author: "Takehiko TERADA"
date: 2021-03-20
lastmod: 2021-03-20
tags: [ailia-sdk]
original_url: https://medium.com/axinc-ai/released-ailia-sdk-1-2-6-1f81eaa27314
---

# Released ailia SDK 1.2.6

# Released ailia SDK 1.2.6

[![Takehiko TERADA](../images/released-ailia-sdk-1-2-6-1f81eaa27314/image_000.jpeg)](/@terada_80332?source=post_page---byline--1f81eaa27314---------------------------------------)

[Takehiko TERADA](/@terada_80332?source=post_page---byline--1f81eaa27314---------------------------------------)

3 min read

·

Mar 20, 2021

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D1f81eaa27314&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Freleased-ailia-sdk-1-2-6-1f81eaa27314&source=---header_actions--1f81eaa27314---------------------post_audio_button------------------)

Share

Introducing version 1.2.6 of [ailia SDK](https://ailia.jp/en/), a cross-platform, GPU-enabled, fast AI inference framework.

---

## Added the ability to omit prototxt when using ONNX.

Added the ability to omit the prototxt when using ONNX. Previously, ONNX was instantiated as follows.

> net = ailia.Net(“a.onnx.prototxt”,”a.onnx”)

Since ailia SDK 1.2.6, prototxt can be omitted as follows.

> net = ailia.Net(None,”a.onnx”)

For Unity, specify null.

> model.OpenFile(null,”a.onnx”)

In the case of C/C++, simply omit ailiaOpenStreamFile.

## Enhanced layer support

We have added 5D input support for Softmax, ReduceSum, and Gather, 1D input support for Deconvolution. We also added Metal support for Space2Depth, 3DConvolution, and Split on macOS. This will allow you to run a wider range of models faster.

## Add run API to ailia Python API

In order to improve consistency with ONNX Runtime, a new run API has been added. In the case of the conventional ailia predict API, if the input is a Tensor, the output is also a Tensor, and if the input is an Array, the output is also an Array, but with the new run API, the output is always an Array.

## PoseEstimator API has been optimized for speed

The pre-processing and post-processing code included in the ailia PoseEstimator API has been optimized for speed. In the RTX2080 environment, LightWeightHumanPoseEstimation runs in about 12ms, enabling real-time skeleton detection.

## Support for new AI models

The following models compatible with 1.2.6 have been added to ailia MODELS. ailia SDK now supports more than 100 models, bringing the total to 110 models.

3dmpe posenet : 3D skeletal estimation

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-6-1f81eaa27314/image_001.png)

Quotation：<https://github.com/mks0601/3DMPPE_POSENET_RELEASE>

[## axinc-ai/ailia-models

### (from https://github.com/mks0601/3DMPPE\_POSENET\_RELEASE/tree/master/demo) Automatically downloads the onnx and prototxt…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/pose_estimation/3dmppe_posenet?source=post_page-----1f81eaa27314---------------------------------------)

Efficient pose : 2D skeleton estimation

[## axinc-ai/ailia-models

### (Image from https://github.com/daniegr/EfficientPose/blob/master/utils/MPII.jpg) Model variant: RT Ailia input shape …

github.com](https://github.com/axinc-ai/ailia-models/tree/master/pose_estimation/efficientpose?source=post_page-----1f81eaa27314---------------------------------------)

Person reid baseline : Same person determination

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-6-1f81eaa27314/image_002.png)

Quotation：<https://github.com/layumi/Person_reID_baseline_pytorch>

[## axinc-ai/ailia-models

### (Image from http://188.138.127.15:81/Datasets/Market-1501-v15.09.15.zip) Shape : (batch, 3, height, width)…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_tracking/person_reid_baseline_pytorch?source=post_page-----1f81eaa27314---------------------------------------)

Source seperation : separation of sound sources

[## axinc-ai/ailia-models

### Noisy speech (audio file) Audio from creative commons youtube videos…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/unet_source_separation?source=post_page-----1f81eaa27314---------------------------------------)

Yet-Another-Anime-Segmenter : Segmentation of Anime style Images

[## axinc-ai/ailia-models

### (Image from https://unity-chan.com/download/index.php and licensed under © Unity Technologies Japan/UCL) ailia input…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/image_segmentation/yet-another-anime-segmenter?source=post_page-----1f81eaa27314---------------------------------------)

EAST : Extract text area

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-6-1f81eaa27314/image_003.png)

Quotation：https://github.com/argman/EAST

Style2paints : Auto Color

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-6-1f81eaa27314/image_004.png)

Quotation：https://github.com/lllyasviel/style2paints

Crnn.pytorch : OCR for English

[## axinc-ai/ailia-models

### (Image above is from https://github.com/meijieru/crnn.pytorch.) The output character will be printed. Automatically…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/text_recognition/crnn.pytorch?source=post_page-----1f81eaa27314---------------------------------------)

deep-text-recognition-benchmark : English OCR

[## axinc-ai/ailia-models

### Pretrained models for ailia SDK. Contribute to axinc-ai/ailia-models development by creating an account on GitHub.

github.com](https://github.com/axinc-ai/ailia-models/tree/master/text_recognition/deep-text-recognition-benchmark?source=post_page-----1f81eaa27314---------------------------------------)

PointNet.pytorch : Segmentation of point clouds

![](../images/released-ailia-sdk-1-2-6-1f81eaa27314/image_005.png)

Quotation：https://github.com/fxia22/pointnet.pytorch

[## axinc-ai/ailia-models

### (Image from http://web.stanford.edu/~ericyi/project\_page/part\_annotation/index.html) Segmentation model Input Shape …

github.com](https://github.com/axinc-ai/ailia-models/tree/master/point_segmentation/pointnet_pytorch?source=post_page-----1f81eaa27314---------------------------------------)

Pixel-Link : Text area extraction

[## axinc-ai/ailia-models

### (Image from https://rrc.cvc.uab.es/?ch=4&com=downloads) Shape : (height, width, 3) pixel\_pos\_scores shape : (1, 192…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/text_detection/pixel_link?source=post_page-----1f81eaa27314---------------------------------------)

Pytorch-dc-tts : Speech Synthesis Model for English

[## axinc-ai/ailia-models

### A sentence which is defined as SENTENCE in pytorch-dc-tts.py. The Voice file is output as .wav which path is defined as…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/pytorch-dc-tts?source=post_page-----1f81eaa27314---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed the ailia SDK, which enables cross-platform, GPU-based rapid inference. ax Inc. provides a wide range of services from consulting, model creation, SDK provision of SDKs, development of AI-based applications and systems, to support Please feel free to [contact us](https://docs.google.com/forms/d/e/1FAIpQLSdZNX-_Z5NJD8qNLOWsiNaPocOMUEfezwfhEusb_C83WeljwA/viewform) as we offer a total solution for.