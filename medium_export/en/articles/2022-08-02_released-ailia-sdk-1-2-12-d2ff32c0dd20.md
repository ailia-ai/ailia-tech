---
title: "Released ailia SDK 1.2.12"
author: "David Cochard"
date: 2022-08-02
lastmod: 2022-09-30
tags: [ailia-sdk, machine-learning, deep-learning, ai]
original_url: https://medium.com/axinc-ai/released-ailia-sdk-1-2-12-d2ff32c0dd20
---

# Released ailia SDK 1.2.12

# Released ailia SDK 1.2.12

[![David Cochard](../images/released-ailia-sdk-1-2-12-d2ff32c0dd20/image_000.jpg)](/@cochard-dav?source=post_page---byline--d2ff32c0dd20---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--d2ff32c0dd20---------------------------------------)

3 min read

·

Aug 2, 2022

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dd2ff32c0dd20&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Freleased-ailia-sdk-1-2-12-d2ff32c0dd20&source=---header_actions--d2ff32c0dd20---------------------post_audio_button------------------)

Share

We are pleased to introduce version 1.2.12 of ailia SDK, a cross-platform framework to perform fast AI inference on GPU or CPU. You can find more information about ailia SDK on the [official website](https://ailia.jp/en/).

![](../images/released-ailia-sdk-1-2-12-d2ff32c0dd20/image_001.png)

## Optimisation of specific activation functions

We developed optimized implementations for activation functions such as *SiLU* used for [YOLOX](/axinc-ai/yolox-object-detection-model-exceeding-yolov5-d6cea6d3c4bc) and [YOLOv5](/axinc-ai/yolov5-the-latest-model-for-object-detection-b13320ec516b), or *Mish* used in [YOLOv4](/axinc-ai/yolov4-a-machine-learning-model-to-detect-the-position-and-type-of-an-object-4f108ed0507b) for cuDNN and CPU (SIMD).

In order to reduce memory transfers between CPU and GPU, the cuDNN implementation was extended to support *Resize (Nearest)* and *Transpose* in CUDA.

These optimizations result in 33% speedup for YOLOX tiny, 18% for YOLOX, 25% for YOLOv5, and 15% for YOLOv4 on Jetson NX using cuDNN. On Intel CPUs using SIMD, YOLOX tiny is 20% faster, 19% for YOLOX, 23% for YOLOv5, and 18% for YOLOv4.

## Faster model loading by sorting graphs in execution order

We have added the ability to sort nodes in execution order when loading graphs to speed up model loading. This speeds up graph exploration and makes loading of huge models such as [*Detic*](/axinc-ai/detic-object-detection-and-segmentation-of-21k-classes-with-high-accuracy-49cba412b7d4)about 30% faster.

## Support for new operators

The support for operators *Compress* and *Det* was added, along with the possibility to have input/output of more than 5 dimensions for the *CumSum* layer.

## Support for ONNX with FP16 weights

ONNX models using FP16 weights can now be loaded in ailia SDK 1.2.12.

## Introduction of new models

- **SberSwap**: Real-time face replacement model

[## ailia-models/generative\_adversarial\_networks/sber-swap at master · axinc-ai/ailia-models

### Source image Target image (Image from https://github.com/ai-forever/sber-swap/tree/main/examples/images) Automatically…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/generative_adversarial_networks/sber-swap?source=post_page-----d2ff32c0dd20---------------------------------------)

- **SwinIR**: Transformer-based super-resolution model

[## ailia-models/super\_resolution/swinir at master · axinc-ai/ailia-models

### In case of classical model. (Image from https://github.com/JingyunLiang/SwinIR/tree/main/testsets) In case of classical…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/super_resolution/swinir?source=post_page-----d2ff32c0dd20---------------------------------------)

- **DabDetr**: Transformer-based object detection model

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-12-d2ff32c0dd20/image_002.png)

Source: <https://github.com/IDEA-opensource/DAB-DETR>

[## ailia-models/object\_detection/dab-detr at master · axinc-ai/ailia-models

### Ailia input shape: (1, 3, 800, 1199) Automatically downloads the onnx and prototxt files on the first run. It is…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/object_detection/dab-detr?source=post_page-----d2ff32c0dd20---------------------------------------)

## Introduction of new samples

Samples of `ailia.audio` were added for Unity and C++ as experimental feature which can be used to classify audio.

[## GitHub — axinc-ai/ailia-audio-samples: ailia.audio samples of unity

### Use ailia.audio to perform MelSpectrum conversion of the input audio. Then classify the sound categories with the crnn…

github.com](https://github.com/axinc-ai/ailia-audio-samples?source=post_page-----d2ff32c0dd20---------------------------------------)

## Evaluation version of ailia SDK

ailia SDK 1.2.12 evaluation version can be downloaded at the link below.

[## ax Inc.

### A future in which all devices carry AI We believe such a future is on the way. To usher in that day, we will keep…

axinc.jp](https://axinc.jp/en/trial/?source=post_page-----d2ff32c0dd20---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.