---
title: "Released ailia SDK 1.2.11"
author: "David Cochard"
date: 2022-05-09
lastmod: 2022-05-09
tags: [ailia-sdk, machine-learning, deep-learning, ai]
original_url: https://medium.com/axinc-ai/released-ailia-sdk-1-2-11-feabe38c8653
---

# Released ailia SDK 1.2.11

# Released ailia SDK 1.2.11

[![David Cochard](../images/released-ailia-sdk-1-2-11-feabe38c8653/image_000.jpg)](/@cochard-dav?source=post_page---byline--feabe38c8653---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--feabe38c8653---------------------------------------)

2 min read

·

May 9, 2022

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dfeabe38c8653&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Freleased-ailia-sdk-1-2-11-feabe38c8653&source=---header_actions--feabe38c8653---------------------post_audio_button------------------)

Share

We are pleased to introduce version 1.2.11 of ailia SDK, a cross-platform framework to perform fast AI inference on GPU or CPU. You can find more information about ailia SDK on the [official website](https://ailia.jp/en/).

![](../images/released-ailia-sdk-1-2-11-feabe38c8653/image_001.png)

## Support for new operators

The support for operators *BitShift、CumSum、GatherElement、ThresholdedRelu* was added, along with the *Sequence* input for *Loop*.

## Faster loading of obfuscated models

The use of AES-NI speeds up the loading of obfuscated models for Windows (Intel), macOS (Intel), Linux (Intel), Android (Arm64) and iOS (Arm64) environments. For example, a 1.24 GB encrypted model can now be loaded 65 times faster.

## Reduced memory consumption of Vulkan

When performing convolution with a large number of channels in Vulkan, memory consumption is reduced by dividing the work memory.

### cuDNN8.3 support

A problem with `ailiaCreate` returning an error when using ailia SDK with cuDNN8.3 was fixed.

### Unity plugin

ailia’s Unity plugin has been upgraded to support Unity 2019.4.32f1 and later. In addition, we have fixed a problem that caused excessive error logs to be displayed when the camera was not available or when the license file did not exist.

### Change Python Environment props to list

Python Environment props is now given as `list`instead of `str` to support multiple flags. No changes to the source code are necessary if you are using the `in` operator as it is done in [*ailia-models*](https://github.com/axinc-ai/ailia-models) samples. The flag `FP16` is now given to props when using *macOS MPS*.

### Evaluation version

Starting with version 1.2.11, the license file is now required for *RaspberryPi* and *Jetson* platforms. The license file must be placed in the `~/.shalo/` folder.

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.