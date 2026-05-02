---
title: "FaceMaskDetection : A Machine Learning Model to Determine if a Person is Wearing a Mask"
author: "David Cochard"
date: 2021-05-24
lastmod: 2021-05-24
tags: [ailia-models, machine-learning, deep-learning, ai]
original_url: https://medium.com/axinc-ai/facemaskdetection-a-machine-learning-model-to-determine-if-a-person-is-wearing-a-mask-e5a581ea8af9
---

# FaceMaskDetection : A Machine Learning Model to Determine if a Person is Wearing a Mask

# FaceMaskDetection : A Machine Learning Model to Determine if a Person is Wearing a Mask

[![David Cochard](../images/facemaskdetection-a-machine-learning-model-to-determine-if-a-person-is-wearing-a-mask-e5a581ea8af9/image_000.jpg)](/@cochard-dav?source=post_page---byline--e5a581ea8af9---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--e5a581ea8af9---------------------------------------)

2 min read

·

May 24, 2021

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3De5a581ea8af9&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Ffacemaskdetection-a-machine-learning-model-to-determine-if-a-person-is-wearing-a-mask-e5a581ea8af9&source=---header_actions--e5a581ea8af9---------------------post_audio_button------------------)

Share

This is an introduction to「FaceMaskDetection」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

Conventional face detection algorithms are trained from unmasked images, so the accuracy of detecting the face position decreases when a mask is worn.

*FaceMaskDetection* is able to detect the position of a face with high accuracy even when a mask is worn, and at the same time determine whether the face is wearing a mask or not.

![](../images/facemaskdetection-a-machine-learning-model-to-determine-if-a-person-is-wearing-a-mask-e5a581ea8af9/image_001.jpeg)

Input image（Source：<https://pixabay.com/ja/photos/%E3%83%95%E3%82%A7%E3%83%AA%E3%83%BC-%E8%88%B9-%E4%B9%97%E5%AE%A2-%E3%82%AF%E3%83%AB%E3%83%BC%E3%82%BA-5484417/>）

![](../images/facemaskdetection-a-machine-learning-model-to-determine-if-a-person-is-wearing-a-mask-e5a581ea8af9/image_002.png)

Result

## Architecture

*FaceMaskDetection* architecture uses [*YOLOv3 Tiny*](/axinc-ai/yolov3-a-machine-learning-model-to-detect-the-position-and-type-of-an-object-60f1c18f8107) and [*MobilenetSSD*](/axinc-ai/mobilenetssd-a-machine-learning-model-for-fast-object-detection-37352ce6da7d), the model has been trained at [ax Inc](https://axinc.jp/en/). In addition to normal face images, we added images of masked faces to the learning process to determine whether a person is wearing a mask or not.

## Usage

You can see how to use *FaceMaskDetection* with the sample code below.

[## axinc-ai/ailia-models

### (Images from…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/face_detection/face-mask-detection?source=post_page-----e5a581ea8af9---------------------------------------)

The following command can be used to determine whether or not a mask is worn or not to any image. By default, [*yolov3-tiny*](/axinc-ai/yolov3-a-machine-learning-model-to-detect-the-position-and-type-of-an-object-60f1c18f8107) is used.

```
$ python3 face-mask-detection.py -i input.png -s output.png
```

The following command runs the model on the web camera video stream.

```
$ python3 face-mask-detection.py -v 0
```

Add the parameter `-a mb2-ssd` to run the model using [*mobilenet-ssd*](/axinc-ai/mobilenetssd-a-machine-learning-model-for-fast-object-detection-37352ce6da7d)*.*

```
$ python3 face-mask-detection.py -v 0 -a mb2-ssd
```

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.