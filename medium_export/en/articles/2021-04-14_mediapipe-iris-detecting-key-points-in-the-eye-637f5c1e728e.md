---
title: "MediaPipe Iris: Detecting Key Points in the Eye"
author: "David Cochard"
date: 2021-04-14
lastmod: 2021-04-29
tags: [ailia-models, machine-learning, deep-learning, ai]
original_url: https://medium.com/axinc-ai/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e
---

# MediaPipe Iris: Detecting Key Points in the Eye

# MediaPipe Iris: Detecting Key Points in the Eye

[![David Cochard](../images/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e/image_000.jpg)](/@cochard-dav?source=post_page---byline--637f5c1e728e---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--637f5c1e728e---------------------------------------)

3 min read

·

Apr 14, 2021

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D637f5c1e728e&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fmediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e&source=---header_actions--637f5c1e728e---------------------post_audio_button------------------)

Share

This is an introduction to「MediaPipe Iris」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

*MediaPipe Iris*, released by Google in August 2020, is a machine learning model for detecting keypoints in a person’s eye. It can be used to recognize where you are looking, estimate distance based on eye size, detect if you are sleeping, etc.

![](../images/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e/image_001.png)

Source：<https://ai.googleblog.com/2020/08/mediapipe-iris-real-time-iris-tracking.html>

[## MediaPipe Iris: Real-time Iris Tracking & Depth Estimation

### A wide range of real-world applications, including computational photography (e.g., portrait mode and glint…

ai.googleblog.com](https://ai.googleblog.com/2020/08/mediapipe-iris-real-time-iris-tracking.html?source=post_page-----637f5c1e728e---------------------------------------)

## Architecture

*MediaPipe Iris* consists of the following three models.

- *BlazeFace* for detecting the position of a face
- *FaceMesh* for detecting keypoints of the face (see details [here](/axinc-ai/facemesh-detecting-key-points-on-faces-in-real-time-977c03f1bab))
- *MediaPipe Iris* for detecting eye keypoints.

First, *BlazeFace* is used to detect the position of the face in the input image, then *FaceMesh* is used to compute 468 keypoints on the detected face, and finally the position of the eyes are computed.

Press enter or click to view image in full size

![](../images/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e/image_002.png)

Input image（Source：<https://pixabay.com/ja/videos/%E5%A5%B3%E6%80%A7-%E3%83%A4%E3%83%B3%E3%82%B0-%E8%B1%AA%E8%8F%AF%E3%81%A7%E3%81%99-%E8%A1%A8%E7%8F%BE-32387/>）

Press enter or click to view image in full size

![](../images/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e/image_003.png)

Face position and keypoints

For the detected eye image, MediaPipe Iris detects 71 *eye key points* and 5 *pupil key points*.

Press enter or click to view image in full size

![](../images/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e/image_004.png)

Key points of the pupil

The model architecture of MediaPipe Iris is based on `MobileNet`, which is a combination of *Convolution*, *DepthwiseConvolution*, and *PRelu*. The input image size is 64x64.

![](../images/mediapipe-iris-detecting-key-points-in-the-eye-637f5c1e728e/image_005.png)

Netron visualization of MediaPipe Iris

## Usage

You can use the following command to run the model on the web camera video stream.

```
$ python3 mediapipe_iris.py --video 0
```

[## axinc-ai/ailia-models

### (Image from https://pixabay.com/photos/person-human-male-face-man-view-829966/) ailia input shape: (1, 3, 128, 128) RGB…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/face_recognition/mediapipe_iris?source=post_page-----637f5c1e728e---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.