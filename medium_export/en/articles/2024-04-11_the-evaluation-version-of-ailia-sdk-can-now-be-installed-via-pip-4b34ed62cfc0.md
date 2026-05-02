---
title: "The evaluation version of ailia SDK can now be installed via pip"
author: "Kazuki Kyakuno"
date: 2024-04-11
lastmod: 2024-05-23
tags: [ailia-sdk]
original_url: https://medium.com/axinc-ai/the-evaluation-version-of-ailia-sdk-can-now-be-installed-via-pip-4b34ed62cfc0
---

# The evaluation version of ailia SDK can now be installed via pip

# The evaluation version of ailia SDK can now be installed via pip

[![Kazuki Kyakuno](../images/the-evaluation-version-of-ailia-sdk-can-now-be-installed-via-pip-4b34ed62cfc0/image_000.png)](/@kyakuno?source=post_page---byline--4b34ed62cfc0---------------------------------------)

[Kazuki Kyakuno](/@kyakuno?source=post_page---byline--4b34ed62cfc0---------------------------------------)

3 min read

·

Apr 11, 2024

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D4b34ed62cfc0&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Fthe-evaluation-version-of-ailia-sdk-can-now-be-installed-via-pip-4b34ed62cfc0&source=---header_actions--4b34ed62cfc0---------------------post_audio_button------------------)

Share

The evaluation version of the ailia SDK is now available for installation via pip, making it easier than ever to introduce and evaluate the ailia SDK.

---

## Installation of the ailia SDK evaluation version via pip

Pip is a package management tool that is standardly used in Python. Traditionally, downloading the evaluation version of the ailia SDK required downloading the SDK from the evaluation version request page. Starting today, it is now possible to install the evaluation version of the ailia SDK via pip, making it easier to introduce and evaluate the ailia SDK.

Press enter or click to view image in full size

![](../images/the-evaluation-version-of-ailia-sdk-can-now-be-installed-via-pip-4b34ed62cfc0/image_001.png)

ailia x pypi

## How to install via pip

Simply execute the following command, and you can install the evaluation version of ailia SDK.

```
pip3 install ailia
```

The supported platforms are Windows, macOS, Linux, Raspberry Pi, and Jetson.

When you run the evaluation version of the ailia SDK, it will automatically download a 30-day evaluation license from the cloud. The license is automatically renewed every 30 days.

## How to use ailia MODELS

By using ailia MODELS, it is possible to run over 300 AI models.

Clone the ailia MODELS repository.

```
git clone https://github.com/axinc-ai/ailia-models.git
```

[## GitHub — axinc-ai/ailia-models: The collection of pre-trained, state-of-the-art AI models for ailia…

### The collection of pre-trained, state-of-the-art AI models for ailia SDK — axinc-ai/ailia-models

github.com](https://github.com/axinc-ai/ailia-models?source=post_page-----4b34ed62cfc0---------------------------------------)

Install the dependent libraries.

```
pip3 install -r requirements.txt
```

Launch the launcher.

```
python3 launchar.py
```

When you select the model you want to execute and press the “Run model” button, the model becomes executable.

Press enter or click to view image in full size

![](../images/the-evaluation-version-of-ailia-sdk-can-now-be-installed-via-pip-4b34ed62cfc0/image_002.png)

## How to Run on Google Colaboratory

With the start of distribution via pip for ailia SDK, it has become possible to use ailia SDK and ailia MODELS on Google Colaboratory as well. Please refer to the following for an example of running on Google Colaboratory.

[## ailia-models/hello\_ailia.ipynb at master · axinc-ai/ailia-models

### The collection of pre-trained, state-of-the-art AI models for ailia SDK - ailia-models/hello\_ailia.ipynb at master ·…

github.com](https://github.com/axinc-ai/ailia-models/blob/master/hello_ailia.ipynb?source=post_page-----4b34ed62cfc0---------------------------------------)

## Expansion of the free usage range of ailia SDK for individual use

We have expanded the scope of personal use of the ailia SDK, and it is now available for free for non-commercial use by individuals.

Please refer to the following page for the Q&A on license conditions.

[## ailia SDK License

### ailia SDK License Information [Japanese] [English] About license !! CAUTION !! "ailia" IS NOT OPEN SOURCE SOFTWARE…

ailia.ai](https://ailia.ai/license/en/?source=post_page-----4b34ed62cfc0---------------------------------------)

---

ax Inc. is developing the ailia SDK, which enables fast inference using GPUs across platforms, as a company that commercializes AI. At ax Corporation, we offer a total solution for AI, ranging from consulting, model creation, providing SDKs, to developing applications and systems utilizing AI, and support. Please feel free to [contact us](https://www.ailia.ai/en-contact-product).