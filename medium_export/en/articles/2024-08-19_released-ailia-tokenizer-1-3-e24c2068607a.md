---
title: "Released ailia Tokenizer 1.3"
author: "David Cochard"
date: 2024-08-19
lastmod: 2024-08-19
tags: [ailia-sdk, machine-learning, ai, nlp]
original_url: https://medium.com/axinc-ai/released-ailia-tokenizer-1-3-e24c2068607a
---

# Released ailia Tokenizer 1.3

# Released ailia Tokenizer 1.3

[![David Cochard](../images/released-ailia-tokenizer-1-3-e24c2068607a/image_000.jpg)](/@cochard-dav?source=post_page---byline--e24c2068607a---------------------------------------)

[David Cochard](/@cochard-dav?source=post_page---byline--e24c2068607a---------------------------------------)

3 min read

·

Aug 19, 2024

--

[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3De24c2068607a&operation=register&redirect=https%3A%2F%2Fmedium.com%2Faxinc-ai%2Freleased-ailia-tokenizer-1-3-e24c2068607a&source=---header_actions--e24c2068607a---------------------post_audio_button------------------)

Share

We have released *ailia Tokenizer 1.3*, which enables mutual conversion between text and tokens. We have also introduced a new Python API and applied it to [ailia MODELS](https://github.com/axinc-ai/ailia-models).

---

## Overview

*ailia Tokenizer* is a library that converts text to tokens and vice versa. When performing natural language processing with AI, it’s necessary to use a tokenizer to convert the text into tokens that the AI can process. Traditionally, this task was handled by [Transformers](https://huggingface.co/docs/transformers/en/index), but since Transformers only offer a Python API, it was challenging to use them from C++, Unity, or Flutter. *ailia Tokenizer* addresses this issue by providing a tokenizer available across multiple platforms.

![](../images/released-ailia-tokenizer-1-3-e24c2068607a/image_001.png)

## New features

### Addition of new tokenizers

We have added support for new tokenizers, including GPT2 and LLAMA. GPT2 is utilized in GPT2, MSCLAP, and BLIP2, while LLAMA is used in llava.

### Performance Optimization

We have optimized the BPE logic for [*Whisper*](/axinc-ai/whisper-speech-recognition-model-capable-of-recognizing-99-languages-5b5cf0197c16)and [*Clip*](/axinc-ai/clip-learning-transferable-visual-models-from-natural-language-supervision-4508b3f0ea46), resulting in a significant gain in processing speed.

### Python API support

A Transformers-compatible API has been added, allowing it to be called directly from Python. Since Transformers use TensorFlow and Torch as backends, they present the following challenges:

- Loading the libraries takes considerable time.
- When used in Docker, the image size becomes large.
- The cuDNN version used by Torch may conflict with the cuDNN versions used by ailia SDK or ONNX Runtime.
- Changes in the Transformers API specifications can cause models to stop working, even with the same arguments.

*ailia Tokenizer* resolves these issues by providing a stable tokenizer with minimal dependencies.

## Usage with ailia MODELS

With the provision of the ailia Tokenizer Python API, all models in ailia MODELS now use *ailia Tokenizer* instead of *Transformers*.

[## GitHub — axinc-ai/ailia-models: The collection of pre-trained, state-of-the-art AI models for ailia…

### The collection of pre-trained, state-of-the-art AI models for ailia SDK — axinc-ai/ailia-models

github.com](https://github.com/axinc-ai/ailia-models?source=post_page-----e24c2068607a---------------------------------------)

Out of the 336 models in ailia MODELS at the time of writing, the following 39 models utilize ailia Tokenizer.

```
audio_processing/clap  
audio_processing/distil-whisper  
audio_processing/msclap  
audio_processing/kotoba-whisper  
diffusion/latent-diffusion-txt2img  
diffusion/stable-diffusion-txt2img  
diffusion/control_net  
diffusion/riffusion  
diffusion/marigold  
image_captioning/blip2  
image_classification/japanese-stable-clip-vit-l-16  
image_classification/japanese-clip  
large_language_model/llava  
natural_language_processing/bert  
natural_language_processing/bert_insert_punctuation  
natural_language_processing/bert_maskedlm  
natural_language_processing/bert_ner  
natural_language_processing/bert_sentiment_analysis  
natural_language_processing/bert_tweet_sentiment  
natural_language_processing/bertjsc  
natural_language_processing/cross_encoder_mmarco  
natural_language_processing/fugumt-en-ja  
natural_language_processing/fugumt-ja-en  
natural_language_processing/multilingual-e5  
natural_language_processing/sentence_transformers_japanese  
natural_language_processing/t5_base_japanese_title_generation  
natural_language_processing/bert_sum_ext  
natural_language_processing/bert_zero_shot_classification  
natural_language_processing/t5_base_japanese_summarization  
natural_language_processing/t5_whisper_medical  
natural_language_processing/gpt2  
natural_language_processing/rinna  
natural_language_processing/bert_question_answering  
natural_language_processing/glucose  
natural_language_processing/bert_maskedlm_proofreeding  
natural_language_processing/soundchoice-g2p  
network_intrucation_detection/bert-network-packet-flow-header-payload  
network_intrucation_detection/falcon-adapter-network-packet  
object_detection/glip
```

You can still use Transformers as before by using the options below.

```
--disable_ailia_tokenizer
```

## More info on ailia Tokenizer

For more information on ailia Tokenizer, please refer to the article below.

[## ailia Tokenizer : NLP Tokenizer for Unity and C++

### Introducing ailia Tokenizer, a tokenizer for NLP that can be used from Unity or C++, without the need for an Python…

medium.com](/axinc-ai/ailia-tokenizer-nlp-tokenizer-for-unity-and-c-e8c3625f9877?source=post_page-----e24c2068607a---------------------------------------)

---

[ax Inc.](https://axinc.jp/en/) has developed [ailia SDK](https://ailia.jp/en/), which enables cross-platform, GPU-based rapid inference.

ax Inc. provides a wide range of services from consulting and model creation, to the development of AI-based applications and SDKs. Feel free to [contact us](https://axinc.jp/en/) for any inquiry.