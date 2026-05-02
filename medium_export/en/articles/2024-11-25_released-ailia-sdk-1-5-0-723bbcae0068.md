---
title: "Released ailia SDK 1.5.0"
author: "David Cochard"
date: 2024-11-25
lastmod: 2024-11-25
tags: [ailia-sdk, machine-learning, ai]
original_url: https://medium.com/axinc-ai/released-ailia-sdk-1-5-0-723bbcae0068
---

# Released ailia SDK 1.5.0

# Released ailia SDK 1.5.0

[![David Cochard](../images/released-ailia-sdk-1-5-0-723bbcae0068/image_000.jpg)](/@cochard-dav?source=post_page---byline--723bbcae0068---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--723bbcae0068---------------------------------------)

3 min read

·

Nov 25, 2024

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D723bbcae0068&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Freleased-ailia-sdk-1-5-0-723bbcae0068&source=---header_actions--723bbcae0068---------------------post_audio_button------------------)

Share

![](../images/released-ailia-sdk-1-5-0-723bbcae0068/image_001.png)

## Speeding up Transformer models

We optimized the speed of the Attention mechanism used in Transformer models. When converted to ONNX, Attention is decomposed into multiple operators, but ailia SDK merges these operators at runtime to speed up the processing.

ailia SDK 1.5.0 achieves faster Attention performance for both CPU (AVX, NEON) and GPU (cuDNN). We are also planning to extend this optimization to other environments in the future.

Below is a speed comparison for the voice synthesis model [GPT-SoVITS](/axinc-ai/gpt-sovits-a-zero-shot-speech-synthesis-model-with-customizable-fine-tuning-e4c72cd75d87). We can see a faster inference than ONNX Runtime on both CPU and CUDA. The ONNX Runtime with CUDA backend struggles with models that involve dynamically changing shapes, often resulting in faster performance on CPU. However, with ailia SDK CUDA backend, even models with dynamically changing shapes can achieve high-speed inference.

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-5-0-723bbcae0068/image_002.png)

## Support for VK\_KHR\_cooperative\_matrix

To accelerate the `MatMul` operation used in Transformer models, we have implemented support for Vulkan operator`VK_KHR_cooperative_matrix`.

`VK_KHR_cooperative_matrix` is an API designed to leverage matrix computation hardware, such as Intel's XMX and NVIDIA's TensorCore. This specialized hardware enables faster inference compared to computing matrix multiplication within shaders.

This feature can be enabled by selecting the Vulkan (FP16) backend.

## Support of opset = 20

The supported range of opsets has been expanded to 20. This allows compatibility with models that can only be exported with opset 20, such as LivePortrait.

## Support of Jetpack 6.0 and 6.1

We have added support for Jetpack 6.0 + cuDNN 8.9.4 and Jetpack 6.1 + cuDNN 9.0.0 on Jetson devices. This ensures that ailia SDK can be used with the latest Jetpack versions.

## Support of numpy 2.0

The Python Binding now supports numpy 2.0. ailia SDK can be used with both numpy 1.x and numpy 2.x using a common binary, ensuring stable operation across versions.

## How to update from ailia SDK 1.4 to 1.5

### Python

You can update ailia SDK using the following `pip` command. Up to ailia SDK 1.4, a common *Wheel* was used for all platforms, but starting from ailia SDK 1.5, platform-specific *Wheels* will be downloaded.

> pip3 install -U ailia

The SDK package can be updated using the following method:

> python3 bootstrap.py  
> pip3 install .

### Unity

You can update ailia SDK via the Package Manager.

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-5-0-723bbcae0068/image_003.png)

### Flutter

The easiest way to update ailia SDK is using the following command:

> flutter pub upgrade

For the official release, replace the libraries in the package with the license-locked versions of `ailia.dll`, `libailia.so`, or `libailia.dylib`.

## Newly supported models

### Live Portrait (Animation of still images)

Bring still portrait images to life

[## ailia-models/generative\_adversarial\_networks/live\_portrait at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK …

github.com](https://github.com/axinc-ai/ailia-models/tree/master/generative_adversarial_networks/live_portrait?source=post_page-----723bbcae0068---------------------------------------)

![](../images/released-ailia-sdk-1-5-0-723bbcae0068/image_004.gif)

出典：<https://github.com/KwaiVGI/LivePortrait>

### Qwen2VL (Vision language model)

High performance VLM that also supports Japanese language.

[## ailia-models/vision\_language\_model/qwen2\_vl at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK — ailia-models/vision\_language\_model/qwen2\_vl…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/vision_language_model/qwen2_vl?source=post_page-----723bbcae0068---------------------------------------)

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-5-0-723bbcae0068/image_005.jpeg)

Source: <https://github.com/QwenLM/Qwen2-VL>

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.