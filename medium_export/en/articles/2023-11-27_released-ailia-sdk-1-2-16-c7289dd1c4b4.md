---
title: "Released ailia SDK 1.2.16"
author: "David Cochard"
date: 2023-11-27
lastmod: 2023-11-27
tags: [ailia-sdk, machine-learning, deep-learning, ai]
original_url: https://medium.com/axinc-ai/released-ailia-sdk-1-2-16-c7289dd1c4b4
---

# Released ailia SDK 1.2.16

# Released ailia SDK 1.2.16

[![David Cochard](../images/released-ailia-sdk-1-2-16-c7289dd1c4b4/image_000.jpg)](/@cochard-dav?source=post_page---byline--c7289dd1c4b4---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--c7289dd1c4b4---------------------------------------)

3 min read

·

Nov 27, 2023

--

1

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc7289dd1c4b4&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Freleased-ailia-sdk-1-2-16-c7289dd1c4b4&source=---header_actions--c7289dd1c4b4---------------------post_audio_button------------------)

Share

We are pleased to introduce version 1.2.16 of ailia SDK, a cross-platform framework to perform fast AI inference on GPU or CPU. You can find more information about ailia SDK on the [official website](https://ailia.jp/en/).

![](../images/released-ailia-sdk-1-2-16-c7289dd1c4b4/image_001.png)

## FP16 support for Vulkan

FP16 mode is now supported when using Vulkan to speed up inference in environments with limited memory bandwidth, such as mobile GPUs.

For example, when inferring *YOLOX-S* with Mali-G78, it takes 156 ms with FP32, but 117 ms with FP16.

Vulkan 1.2 or later is required to use FP16. Vulkan 1.3 is the standard for Android 13 or later, so it can be used as standard on those devices.

## Lower memory footprint

The memory usage was reduced by freeing up CPU memory after weights are transferred to the GPU. In addition, the algorithm allowing memory reuse for cuDNN has been improved to allow more GPU memory to be efficiently reused.

## Support for ONNX over 2GB

Support for loading external *pb* was added, allowing for loading ONNX over 2 GB.

## Voice processing optimization

Performance of the voice processing model has been improved by optimizing the processing of `Concat`, which has a small number of channels, and `Conv1D`, which has a large kernel size. As a result CPU inference for [Crepe](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/crepe) is about 2.6 times faster, and the CPU inference for [RVC](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/rvc) is also speeded up by approximately 20%.

## Support for opset17

`LayerNormalization` in opset17 is now supported. This allows inference of voice models using this operator, such as models exported with slightly older [RVC](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/rvc).

## Addition of ailia.js

The `ailia.js` library is now officially supported to perform inference in thee web browser. More details on `ailia.js` can be found below.

[## ailia.js: a library to execute ML models inside the browser

### In this article I will present you ailia.js, a AI inference engine that runs inside the browser. This library allows…

medium.com](/axinc-ai/ailia-js-a-library-to-execute-ml-models-inside-the-browser-e179c99c5b19?source=post_page-----c7289dd1c4b4---------------------------------------)

## New models available in ailia SDK 1.2.16

Thanks to the support of external pb explained above, we now support much larger models to run.

### SegmentAnything: high-quality segmentation model by Meta

[## ailia-models/image\_segmentation/segment-anything at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK …

github.com](https://github.com/axinc-ai/ailia-models/tree/master/image_segmentation/segment-anything?source=post_page-----c7289dd1c4b4---------------------------------------)

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-16-c7289dd1c4b4/image_002.png)

Segmentation by coordinates ( Source: <https://github.com/facebookresearch/segment-anything/blob/main/notebooks/images/truck.jpg>)

### BLIP2: high-precision image captioning model

[## ailia-models/image\_captioning/blip2 at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK — ailia-models/image\_captioning/blip2 at master…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/image_captioning/blip2?source=post_page-----c7289dd1c4b4---------------------------------------)

```
$ python3 blip2.py
```

Press enter or click to view image in full size

![](../images/released-ailia-sdk-1-2-16-c7289dd1c4b4/image_003.png)

BLIP2 example input (Source: <https://github.com/salesforce/LAVIS/blob/main/docs/_static/merlion.png>)

```
### Output ###  
singapore merlion fountain
```

### Whisper Large V2, V3: speech recognition models over 2 GB

[## ailia-models/audio\_processing/whisper at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK — ailia-models/audio\_processing/whisper at…

github.com](https://github.com/axinc-ai/ailia-models/tree/master/audio_processing/whisper?source=post_page-----c7289dd1c4b4---------------------------------------)

```
$ python3 whisper.py -m large-v3
```

### Multilingual E5 Large: latest text embedding model

[## ailia-models/natural\_language\_processing/multilingual-e5 at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK …

github.com](https://github.com/axinc-ai/ailia-models/tree/master/natural_language_processing/multilingual-e5?source=post_page-----c7289dd1c4b4---------------------------------------)

```
$ python3 multilingual-e5.py -m large
```

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.