---
title: "U2Net : A machine learning model that performs object cropping in a single shot"
author: "Kazuki Kyakuno"
date: 2020-12-02
lastmod: 2021-09-21
tags: [ailia-models]
original_url: https://medium.com/axinc-ai/u2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483
---

# U2Net : A machine learning model that performs object cropping in a single shot

# U2Net : A machine learning model that performs object cropping in a single shot

[![Kazuki Kyakuno](../images/u2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483/image_000.png)](/@kyakuno?source=post_page---byline--48adfc158483---------------------------------------)

[Kazuki Kyakuno](/@kyakuno?source=post_page---byline--48adfc158483---------------------------------------)

3 min read

·

Dec 2, 2020

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D48adfc158483&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fu2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483&source=---header_actions--48adfc158483---------------------post_audio_button------------------)

Share

Introducing U2Net, a machine learning model that can be used with ailia SDK. You can easily implement AI features in your applications by using the machine learning models published in [ailia SDK](https://ailia.jp/en/) and [ailia MODELS](https://github.com/axinc-ai/ailia-models), which is a reasoning framework for the edge.

---

## About U2Net

U2Net is a machine learning model that allows you to crop objects in a single shot. Taking an image of a person, cat, etc. as input, it can compute an alpha value to separate the background from the panoramic view. U2Net is available in U2Net with a model size of 176.3 MB and U2NetP with a model size of 4.7 MB.

[## U$²$-Net: Going Deeper with Nested U-Structure for Salient Object Detection

### In this paper, we design a simple yet powerful deep network architecture, U$²$-Net, for salient object detection…

arxiv.org](https://arxiv.org/abs/2005.09007?source=post_page-----48adfc158483---------------------------------------)

Press enter or click to view image in full size

![](../images/u2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483/image_001.png)

（出典：<https://github.com/NathanUA/U-2-Net>）

## Architecture of U2Net

U2Net is a hierarchical structure of UNet, with two connected in series. Conventional models often use Classifier models pre-trained by ImageNet for Backbone, but we propose a model structure optimized for the background separation task, and the performance is comparable to SOTA.

Press enter or click to view image in full size

![](../images/u2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483/image_002.png)

（Source：<https://arxiv.org/abs/2005.09007>）

U2Net is learning in 320x320 resolution.

[## NathanUA/U-2-Net

### The code for our newly accepted paper U²-Net (U square net) in Pattern Recognition 2020: Contact…

github.com](https://github.com/NathanUA/U-2-Net?source=post_page-----48adfc158483---------------------------------------)

U2Net and U2NetP have the same network architecture but differ in the number of input and output FeatureMaps; U2Net extends the number of En.5 FeatureMaps to 512, while U2NetP is limited to 64. Since the number of feature maps is highly dependent on the number of feature maps, the model size can be reduced to 1/37.5 by reducing the number of feature maps.

However, in terms of performance improvement, as shown in the paper, the 30FPS of U2Net on the GeForce GTX 1080Ti is only 1.33 times higher than the 30FPS of U2Net on the GeForce GTX 1080Ti, and 40FPS on U2NetP.

Press enter or click to view image in full size

![](../images/u2net-a-machine-learning-model-that-performs-object-cropping-in-a-single-shot-48adfc158483/image_003.png)

（Source：<https://arxiv.org/abs/2005.09007>）

Learning uses SOD (Salient Object Dataset).

[## Salient Objects Dataset (SOD) — Elder Laboratory

### For each image of the 300 images used in BSD, there is a .mat file which can be opened by Matlab. Loading each mat file…

www.elderlab.yorku.ca](https://www.elderlab.yorku.ca/resources/salient-objects-dataset-sod/?source=post_page-----48adfc158483---------------------------------------)

## How to use U2Net

The ailia SDK allows you to use U2Net in the following samples.

[## ailia-models/background\_removal/u2net at master · axinc-ai/ailia-models

### (Image from https://github.com/NathanUA/U-2-Net/blob/master/test\_data/test\_images/girl.png) Ailia input shape: (1, 3…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/background_removal/u2net?source=post_page-----48adfc158483---------------------------------------)

With the following command, you can use U2Net to crop a person with a web camera as input.

> python3 u2net.py -v 0

If you specify -a small, you can use a small model size U2NetP.

> python3 u2net.py -v 0 -a small

The ailia SDK can be used not only from Python, but also from C and C#, below is an example of using U2Net from Xcode.

[## axinc-ai/ailia-xcode

### Project sample of ailia SDK for xcode Xcode 11.3 Download u2net\_opset11.onnx in ./u2net folder. wget…

github.com](https://github.com/axinc-ai/ailia-xcode?source=post_page-----48adfc158483---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed the ailia SDK, which enables cross-platform, GPU-based rapid inference. ax Inc. provides a wide range of services from consulting, model creation, SDK provision of SDKs, development of AI-based applications and systems, to support Please feel free to [contact us](https://docs.google.com/forms/d/e/1FAIpQLSdZNX-_Z5NJD8qNLOWsiNaPocOMUEfezwfhEusb_C83WeljwA/viewform) as we offer a total solution for.