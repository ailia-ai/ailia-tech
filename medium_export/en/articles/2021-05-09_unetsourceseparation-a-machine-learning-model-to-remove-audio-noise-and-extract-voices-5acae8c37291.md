---
title: "UnetSourceSeparation: A machine learning model to remove audio noise and extract voices"
author: "David Cochard"
date: 2021-05-09
lastmod: 2021-05-09
tags: [ailia-models, machine-learning, deep-learning, audio, ai]
original_url: https://medium.com/axinc-ai/unetsourceseparation-a-machine-learning-model-to-remove-audio-noise-and-extract-voices-5acae8c37291
---

# UnetSourceSeparation: A machine learning model to remove audio noise and extract voices

# UnetSourceSeparation: A machine learning model to remove audio noise and extract voices

[![David Cochard](../images/unetsourceseparation-a-machine-learning-model-to-remove-audio-noise-and-extract-voices-5acae8c37291/image_000.jpg)](/@cochard-dav?source=post_page---byline--5acae8c37291---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--5acae8c37291---------------------------------------)

3 min read

·

May 9, 2021

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D5acae8c37291&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Funetsourceseparation-a-machine-learning-model-to-remove-audio-noise-and-extract-voices-5acae8c37291&source=---header_actions--5acae8c37291---------------------post_audio_button------------------)

Share

This is an introduction to「UnetSourceSeparation」, a machine learning model that can be used with [ailia SDK](https://ailia.jp/en/). You can easily use this model to create AI applications using [ailia SDK](https://ailia.jp/en/) as well as many other ready-to-use [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

*UnetSourceSeparation* is a audio separation model released in March 2019. It can cancel background noise from an input audio file and extract voices.

[## Phase-aware Speech Enhancement with Deep Complex U-Net

### Most deep learning-based models for speech enhancement have mainly focused on estimating the magnitude of spectrogram…

arxiv.org](https://arxiv.org/abs/1903.03107v1?source=post_page-----5acae8c37291---------------------------------------)

## UnetSourceSeparation demonstration

The official demo of voice separation is shown below. The original voice and the processed voice are played alternately.

## Architecture

In speech processing, it is common to perform *Short Time Fourier Transform* (STFT) on the input speech and apply CNN in frequency space. the output of FT (Fourier Transform) is a Complex Value, which consists of Magnitude and Phase.

Phase estimation is difficult, and in conventional speech separation, only Magnitude is estimated. However, when the Phase of the original material is used as it is, there is no problem when the Signal-to-Noise Ratio (SNR) is high (low noise), but when the SNR is low (high noise), there is a problem that noise remains.

Press enter or click to view image in full size

![](../images/unetsourceseparation-a-machine-learning-model-to-remove-audio-noise-and-extract-voices-5acae8c37291/image_001.png)

Source：<https://arxiv.org/pdf/1903.03107v1>

In *UnetSourceSeparation*, the new `Complex Value Convolution` enables Phase prediction.

Press enter or click to view image in full size

![](../images/unetsourceseparation-a-machine-learning-model-to-remove-audio-noise-and-extract-voices-5acae8c37291/image_002.png)

Source：<https://arxiv.org/pdf/1903.03107v1>

The architecture of *UnetSourceSeparation* is as follows. The input audio is processed using STFT to obtain the frequency components and then passed through Unet architecture using Complex Convolution. It then creates a mask and use it to remove the noise, and returns to the waveform using *Inverse Short-Time-Fourier-Transform* (ISTFT).

Press enter or click to view image in full size

![](../images/unetsourceseparation-a-machine-learning-model-to-remove-audio-noise-and-extract-voices-5acae8c37291/image_003.png)

Source：<https://arxiv.org/pdf/1903.03107v1>

The *DSD100* dataset is used for training.

[## DSD100 | SigSep

### The dsd100 is a dataset of 100 full lengths music tracks of different styles along with their isolated drums, bass…

sigsep.github.io](https://sigsep.github.io/datasets/dsd100.html?source=post_page-----5acae8c37291---------------------------------------)

## Usage

Given an input audio file, the output audio file is generated. The default model used it the noise reduction model for voice separation in general speech.

```
$ python3 unet_source_separation.py --input WAV_PATH --savepath SAVE_WAV_PATH
```

To perform voice extraction in a music song, add the parameter `--arch large`

```
$ python3 unet_source_separation.py --input WAV_PATH --savepath SAVE_WAV_PATH --arch large
```

[## axinc-ai/ailia-models

### Noisy speech (audio file) Audio from creative commons youtube videos…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/unet_source_separation?source=post_page-----5acae8c37291---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.